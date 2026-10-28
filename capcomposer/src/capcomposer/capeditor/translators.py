import logging
import re

import requests
from deep_translator import MyMemoryTranslator
from deep_translator.constants import GOOGLE_LANGUAGES_TO_CODES, MY_MEMORY_LANGUAGES_TO_CODES
from django.conf import settings
from django_deep_translator.services import BaseTranslatorService

logger = logging.getLogger(__name__)

GOOGLE_GTX_URL = "https://translate.googleapis.com/translate_a/single"

# MyMemory rejects texts of 500 characters or more
MYMEMORY_MAX_CHARS = 499


def resolve_language(code, supported_codes):
    """
    Map a CAP language code (RFC 3066, e.g. 'en-US' or 'fr') to a code the translator accepts,
    matching on the primary subtag when the exact code is not supported ('en-US' -> 'en', 'fr' -> 'fr-FR').
    """
    if not supported_codes:
        return code

    by_lower = {c.lower(): c for c in supported_codes}
    if code.lower() in by_lower:
        return by_lower[code.lower()]

    primary = code.replace('_', '-').split('-')[0].lower()
    if primary in by_lower:
        return by_lower[primary]

    # Prefer the "main" region variant, e.g. fr-FR over fr-BE
    if f'{primary}-{primary}' in by_lower:
        return by_lower[f'{primary}-{primary}']

    for c in supported_codes:
        if c.lower().split('-')[0] == primary:
            return c

    return code


def split_text(text, max_chars):
    """
    Split text into chunks of at most max_chars, on paragraph, then sentence, then word boundaries.
    Joining the chunks gives back the original text.
    """
    if len(text) <= max_chars:
        return [text]

    for pattern in (r'(?<=\n)', r'(?<=[.!?])(?=\s)', r'(?=\s)'):
        parts = [p for p in re.split(pattern, text) if p]
        if len(parts) > 1:
            break
    else:
        return [text[i:i + max_chars] for i in range(0, len(text), max_chars)]

    chunks = []
    current = ''
    for part in parts:
        if len(part) > max_chars:
            if current:
                chunks.append(current)
                current = ''
            chunks.extend(split_text(part, max_chars))
        elif len(current) + len(part) > max_chars:
            chunks.append(current)
            current = part
        else:
            current += part
    if current:
        chunks.append(current)
    return chunks


def google_gtx_translate(text, target_language, source_language='auto'):
    """
    Translate using Google's free, keyless 'gtx' endpoint (the one used by browser extensions).
    It is undocumented and may be rate limited, so callers should be ready to fall back.
    """
    codes = list(GOOGLE_LANGUAGES_TO_CODES.values())
    target = resolve_language(target_language, codes)
    source = 'auto' if source_language == 'auto' else resolve_language(source_language, codes)

    response = requests.post(
        GOOGLE_GTX_URL,
        params={'client': 'gtx', 'sl': source, 'tl': target, 'dt': 't'},
        data={'q': text},
        timeout=15,
    )
    response.raise_for_status()

    segments = response.json()[0] or []
    translated = ''.join(segment[0] for segment in segments if segment and segment[0])
    if not translated:
        raise ValueError('Google returned an empty translation')
    return translated


def mymemory_translate(text, target_language, source_language='auto'):
    codes = list(MY_MEMORY_LANGUAGES_TO_CODES.values())
    if source_language == 'auto':
        # MyMemory cannot detect the source language
        source_language = getattr(settings, 'LANGUAGE_CODE', 'en')
    translator = MyMemoryTranslator(source=resolve_language(source_language, codes),
                                    target=resolve_language(target_language, codes))

    translated = []
    for chunk in split_text(text, MYMEMORY_MAX_CHARS):
        if not chunk.strip():
            translated.append(chunk)
            continue
        result = translator.translate(chunk)
        # MyMemory returns quota and validation errors as the translated text
        if not result or result.startswith('MYMEMORY WARNING') or 'IS AN INVALID' in result:
            raise ValueError(result or 'MyMemory returned an empty translation')
        # Keep the whitespace around the chunk, which MyMemory strips
        leading = chunk[:len(chunk) - len(chunk.lstrip())]
        trailing = chunk[len(chunk.rstrip()):]
        translated.append(leading + result.strip() + trailing)
    return ''.join(translated)


class GoogleWithMyMemoryFallbackTranslatorService(BaseTranslatorService):
    """
    Free translator that needs no API key: Google's gtx endpoint, falling back to MyMemory
    when Google fails or rate limits.
    """

    def translate_string(self, text, target_language, source_language='auto'):
        try:
            return google_gtx_translate(text, target_language, source_language)
        except Exception as e:
            logger.warning("Google translation failed, falling back to MyMemory: %s", e)

        return mymemory_translate(text, target_language, source_language)
