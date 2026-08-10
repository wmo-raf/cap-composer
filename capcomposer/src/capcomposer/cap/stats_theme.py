"""
Colour resolution for the CAP statistics admin page.

When cap-composer runs inside a ClimWeb deployment, the chart/card colours are
derived from the deployment's active ClimWeb theme (Admin -> Settings -> Theme),
so the page matches the ClimWeb style guide. When cap-composer runs standalone,
the original hard-coded palette is used unchanged.

Severity and status colours are intentionally NOT themed in either mode: they are
CAP-standard semantic colours and must stay comparable across deployments.
"""

from django.apps import apps

# ── Standalone (non-ClimWeb) palette — unchanged from the original template ──
STANDALONE_THEME = {
    "primary": "#2563EB",
    "primary_light": "#e8f0fe",
    "primary_medium": "#93b4f5",
    "background": "#f8f8f8",
    "surface": "#ffffff",
    "border": "#e2e2e2",
    "text": "#1a1a1a",
    "muted": "#666666",
    "border_radius": "8px",
}

STANDALONE_PALETTE = [
    "#2563EB", "#7C3AED", "#059669", "#D97706", "#DC2626",
    "#0891B2", "#65A30D", "#DB2777", "#9333EA", "#EA580C",
]

STANDALONE_URGENCY_COLORS = {
    "Immediate": "#DC2626",
    "Expected": "#D97706",
    "Future": "#2563EB",
    "Past": "#6B7280",
    "Unknown": "#9CA3AF",
}

STANDALONE_CERTAINTY_COLORS = {
    "Observed": "#059669",
    "Likely": "#65A30D",
    "Possible": "#0891B2",
    "Unlikely": "#6B7280",
    "Unknown": "#9CA3AF",
}

UNKNOWN_GREY = "#9CA3AF"


def _mix_with_white(hex_color, amount=0.5):
    """amount = 0.0 -> original colour, 1.0 -> white."""
    hex_color = (hex_color or "").lstrip("#")

    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)

    if len(hex_color) < 6:
        raise ValueError("invalid hex colour")

    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)

    return f"#{r:02x}{g:02x}{b:02x}"


def _get_climweb_theme():
    """
    Return the active ClimWeb Theme instance, or None when cap-composer is not
    running inside a ClimWeb deployment (or no default theme is configured).
    """
    if not apps.is_installed("climweb.base"):
        return None

    try:
        theme_model = apps.get_model("base", "Theme")
        return theme_model.objects.filter(is_default=True).first()
    except Exception:
        return None


def _ramp(primary, count):
    """A monochrome ramp of `count` shades, strongest first."""
    if count <= 0:
        return []
    if count == 1:
        return [primary]

    max_mix = 0.72
    return [
        _mix_with_white(primary, (i / (count - 1)) * max_mix)
        for i in range(count)
    ]


def _ordered_colors(labels, primary, standalone_map):
    """
    Colours for an ordered categorical axis (urgency / certainty).

    Standalone keeps the original semantic colours; themed mode uses a ramp of
    the ClimWeb primary colour. "Unknown" is grey in both modes.
    """
    if primary is None:
        return [standalone_map.get(label, UNKNOWN_GREY) for label in labels]

    known = [label for label in labels if label != "Unknown"]
    ramp = dict(zip(known, _ramp(primary, len(known))))

    return [ramp.get(label, UNKNOWN_GREY) for label in labels]


def get_stats_theme():
    """
    Resolve the colour tokens + derived palettes for the statistics page.

    Returns a dict with a ``themed`` flag, the CSS tokens consumed by
    ``cap/statistics.html``, and the chart palettes.
    """
    climweb_theme = _get_climweb_theme()

    if climweb_theme is None:
        return {
            "themed": False,
            "primary": None,
            "tokens": dict(STANDALONE_THEME),
            "palette": list(STANDALONE_PALETTE),
        }

    try:
        primary = climweb_theme.primary_hover_color
        tokens = {
            "primary": primary,
            "primary_light": _mix_with_white(primary, 0.88),
            "primary_medium": _mix_with_white(primary, 0.50),
            "background": _mix_with_white(primary, 0.94),
            "surface": "#ffffff",
            "border": _mix_with_white(primary, 0.85),
            "text": climweb_theme.primary_color,
            "muted": "#666666",
            "border_radius": f"{climweb_theme.border_radius * 0.06}em",
        }
    except Exception:
        # Malformed theme values — fall back rather than break the page.
        return {
            "themed": False,
            "primary": None,
            "tokens": dict(STANDALONE_THEME),
            "palette": list(STANDALONE_PALETTE),
        }

    return {
        "themed": True,
        "primary": primary,
        "tokens": tokens,
        "palette": _ramp(primary, 10),
    }


def get_urgency_colors(labels, theme):
    return _ordered_colors(labels, theme.get("primary"), STANDALONE_URGENCY_COLORS)


def get_certainty_colors(labels, theme):
    return _ordered_colors(labels, theme.get("primary"), STANDALONE_CERTAINTY_COLORS)


def get_event_colors(labels, theme):
    """Cycle the palette so any number of hazard types gets a colour."""
    palette = theme["palette"]
    return [palette[i % len(palette)] for i in range(len(labels))]
