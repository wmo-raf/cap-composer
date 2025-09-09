import urllib.parse

from django import template

register = template.Library()

DEFAULT_ONLINE_SHARE_CONFIG = [
    {
        "name": "Facebook",
        "base_url": "https://www.facebook.com/sharer/sharer.php",
        "link_param": "u",
        "text_param": "quote",
        "fa_icon": "facebook-f",
        "svg_icon": "facebook",
        "enabled": True
    },
    {
        "name": "X",
        "base_url": "https://twitter.com/intent/post",
        "link_param": "url",
        "text_param": "text",
        "fa_icon": "x-twitter",
        "svg_icon": "x-twitter",
        "enabled": True,
    },
    {
        "name": "LinkedIn",
        "base_url": "https://www.linkedin.com/sharing/share-offsite",
        "link_param": "url",
        "fa_icon": "linkedin-in",
        "svg_icon": "linkedin",
        "enabled": True,
    },
    {
        "name": "WhatsApp",
        "base_url": "https://api.whatsapp.com/send",
        "link_param": "text",
        "encode": True,
        "text_in_url": True,
        "fa_icon": "whatsapp",
        "svg_icon": "whatsapp",
        "enabled": True,
    },
    {
        "name": "Telegram",
        "base_url": "https://t.me/share/url",
        "link_param": "url",
        "text_param": "text",
        "fa_icon": "telegram",
        "svg_icon": "telegram",
        "enabled": True,
    },

]


@register.inclusion_tag("cap/social_media_share_buttons_include.html")
def share_buttons(url, text=None):
    share_urls = []
    for config in DEFAULT_ONLINE_SHARE_CONFIG:
        enabled = config.get('enabled', False)
        name = config.get('name', None)
        base_url = config.get('base_url', None)
        link_param = config.get('link_param', None)
        text_in_url = config.get('text_in_url', False)
        text_param = config.get('text_param', None)
        encode = config.get('encode', False)
        fa_icon = config.get('fa_icon', False)
        svg_icon = config.get('svg_icon', None)
        
        link_query = None
        text_query = None
        
        item_url = url
        item_text = text
        
        if not enabled or not name or not base_url or not link_param:
            continue
        
        if encode:
            item_url = urllib.parse.quote(item_url)
            if item_text:
                item_text = urllib.parse.quote(item_text)
        
        if item_text:
            if text_in_url:
                item_url = f"{item_text}%20{item_url}"
            elif text_param:
                text_query = f"{text_param}={item_text}"
        
        if link_param and item_url:
            link_query = f"{link_param}={item_url}"
        
        share_url = f"{base_url}?{link_query}"
        
        if text_query:
            share_url = f"{share_url}&{text_query}"
        
        share_urls.append({
            'name': name,
            'url': share_url,
            'fa_icon': fa_icon,
            'svg_icon': svg_icon
        })
    
    return {"share_urls": share_urls}
