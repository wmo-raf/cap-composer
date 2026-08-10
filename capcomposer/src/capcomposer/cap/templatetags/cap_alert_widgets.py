"""Template tags for rendering the active-alert nav widget inline.

The widget used to be fetched over AJAX and injected into the navbar after page
load. That broke translation: ClimWeb has no LocaleMiddleware or i18n_patterns,
so visitor-facing language switching is done client-side by the Google Translate
widget, which only rewrites the DOM it sees at load time. Markup injected
afterwards keeps the server language while the chrome around it is translated.

Rendering the widget as part of the initial response puts it in front of the
translator along with everything else.
"""

from django import template
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.safestring import mark_safe

from ..models import OtherCAPSettings
from ..utils import get_currently_active_alerts

register = template.Library()

WIDGET_TEMPLATES = {
    "nav_left": "cap/widgets/nav_left_alert.html",
    "nav_top": "cap/widgets/nav_top_alert.html",
}

DEFAULT_ALERT_STYLE = "nav_left"


def _get_latest_active_alert(request, cap_settings):
    """The first currently-active alert, in the configured display language."""
    default_language = cap_settings.default_alert_display_language

    for alert in get_currently_active_alerts():
        alert_info = alert.infos[0]

        if default_language and len(alert.info) > 1:
            for info_item in alert.infos:
                info_language = info_item.get("info").value.get("language")
                if info_language and (
                    info_language == default_language.code
                    or info_language.startswith(default_language.code)
                ):
                    alert_info = info_item
                    break

        alert_info.update({"title": alert.title})
        return alert_info

    return None


@register.simple_tag(takes_context=True)
def active_alert_widget(context, slot):
    """Render the active-alert widget if `slot` matches the configured style.

    The navbar calls this once per mount point ("nav_top" above the header,
    "nav_left" inside the utility bar); only the slot matching the site's
    Active Alert Style setting renders anything.
    """
    if slot not in WIDGET_TEMPLATES:
        return ""

    request = context.get("request")
    if request is None:
        return ""

    cap_settings = OtherCAPSettings.for_request(request)
    alert_style = cap_settings.active_alert_style or DEFAULT_ALERT_STYLE

    if alert_style != slot:
        return ""

    latest_active_alert = _get_latest_active_alert(request, cap_settings)
    if not latest_active_alert:
        return ""

    return mark_safe(
        render_to_string(
            WIDGET_TEMPLATES[slot],
            {
                "latest_active_alert": latest_active_alert,
                "alert_style": alert_style,
                "request": request,
            },
            request=request,
        )
    )
