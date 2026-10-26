from django.test import SimpleTestCase

from capcomposer.capeditor.constants import SEVERITY_MAPPING


def _luminance(hex_color):
    hex_color = hex_color.lstrip("#")

    def channel(value):
        value = value / 255
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(int(hex_color[i:i + 2], 16)) for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color_a, color_b):
    lighter, darker = sorted((_luminance(color_a), _luminance(color_b)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


class SeverityColorContrastTest(SimpleTestCase):
    """Severity text colours must stay readable (WCAG 2.1 AA, 4.5:1 for normal text)."""

    def test_text_color_is_readable_on_severity_background_and_white(self):
        for name, severity in SEVERITY_MAPPING.items():
            with self.subTest(severity=name):
                self.assertGreaterEqual(contrast_ratio(severity["text_color"], severity["background_color"]), 4.5)
                self.assertGreaterEqual(contrast_ratio(severity["text_color"], "#ffffff"), 4.5)

    def test_white_is_readable_on_text_color(self):
        # the "Alert" badge in the top banner is white text on text_color
        for name, severity in SEVERITY_MAPPING.items():
            with self.subTest(severity=name):
                self.assertGreaterEqual(contrast_ratio("#ffffff", severity["text_color"]), 4.5)

    def test_on_color_text_is_readable_on_severity_color(self):
        for name, severity in SEVERITY_MAPPING.items():
            with self.subTest(severity=name):
                self.assertGreaterEqual(contrast_ratio(severity["on_color_text"], severity["color"]), 4.5)
