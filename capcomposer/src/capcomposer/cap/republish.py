import logging
from datetime import timedelta
from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from wagtail.admin import messages
from wagtail.models import Site
from wagtail_modeladmin.helpers import AdminURLHelper

from .mqtt.models import CAPAlertMQTTBrokerEvent
from .tasks import (
    handle_republish_alert_to_mqtt_broker,
    handle_republish_alert_to_webhook,
)
from .webhook.models import CAPAlertWebhookEvent

logger = logging.getLogger(__name__)

# Number of minutes after which a stuck PENDING attempt is treated as stale
# and no longer blocks a new republish (guards against a dead worker wedging
# the feature).
CAP_REPUBLISH_PENDING_TIMEOUT_MINUTES = getattr(
    settings, "CAP_REPUBLISH_PENDING_TIMEOUT_MINUTES", 10
)


def _mqtt_alert_guard(alert):
    """MQTT dissemination requires the alert to be live, Actual and Public."""
    if not alert.is_published_publicly:
        return _("This alert is no longer live, Actual and Public, and cannot "
                 "be republished to an MQTT broker.")
    return None


def _webhook_alert_guard(alert):
    """Webhook dissemination requires the alert to be live and either Actual
    or Public (mirrors the auto-publish webhook guard)."""
    if not (alert.live and (alert.status == "Actual" or alert.scope == "Public")):
        return _("This alert is no longer eligible (it must be live and either "
                 "Actual or Public) and cannot be republished to a webhook.")
    return None


MQTT_CHANNEL = {
    "model": CAPAlertMQTTBrokerEvent,
    "target_attr": "broker",
    "target_verbose": _("MQTT broker"),
    "guard": _mqtt_alert_guard,
    "task": handle_republish_alert_to_mqtt_broker,
    "republish_url_name": "republish_mqtt_event",
    "events_related_name": "mqtt_broker_events",
}

WEBHOOK_CHANNEL = {
    "model": CAPAlertWebhookEvent,
    "target_attr": "webhook",
    "target_verbose": _("webhook"),
    "guard": _webhook_alert_guard,
    "task": handle_republish_alert_to_webhook,
    "republish_url_name": "republish_webhook_event",
    "events_related_name": "webhook_events",
}


def _safe_redirect_url(request, fallback):
    """Returns the validated ?next= target, or the fallback if absent/unsafe."""
    next_url = request.GET.get("next") or request.POST.get("next")
    if next_url and url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
    ):
        return next_url
    return fallback


def _handle_republish(request, channel, event_id):
    model = channel["model"]
    target_attr = channel["target_attr"]
    
    event = get_object_or_404(model, id=event_id)
    target = getattr(event, target_attr)
    alert = event.alert
    
    # Site scoping: a raw POST/GET with an event id must not reach a target
    # belonging to another site.
    current_site = Site.find_for_request(request)
    current_site_id = current_site.id if current_site else None
    if not target.site_id or target.site_id != current_site_id:
        raise Http404("Event not found for this site")
    
    # Republishing is gated on the right to publish the alert page itself.
    if not alert.permissions_for_user(request.user).can_publish():
        raise PermissionDenied
    
    index_url = AdminURLHelper(model).get_action_url("index")
    redirect_url = _safe_redirect_url(request, index_url)
    
    # Alert-level guard (the target's `active` flag is intentionally NOT
    # checked here — the operator explicitly chose this target).
    guard_error = channel["guard"](alert)
    
    if request.method == "POST":
        if guard_error:
            messages.error(request, guard_error)
            return redirect(redirect_url)
        
        # Refuse if a non-stale republish is already in flight for this target.
        cutoff = timezone.now() - timedelta(minutes=CAP_REPUBLISH_PENDING_TIMEOUT_MINUTES)
        in_flight = model.objects.filter(
            alert=alert,
            status="PENDING",
            created__gte=cutoff,
            **{target_attr: target},
        ).exists()
        if in_flight:
            messages.warning(request, _("A republish is already in progress for "
                                        "this target. Please wait for it to complete."))
            return redirect(redirect_url)
        
        # Every republish roots to the original event. By invariant, an event is
        # either the original (source_event is null) or points straight at it.
        root = event.source_event if event.source_event_id else event
        
        new_event = model.objects.create(
            alert=alert,
            status="PENDING",
            source_event=root,
            **{target_attr: target},
        )
        channel["task"].delay(new_event.id)
        
        messages.success(request, _("Republish queued for %(target)s '%(name)s'.") % {
            "target": channel["target_verbose"],
            "name": str(target),
        })
        return redirect(redirect_url)
    
    context = {
        "event": event,
        "alert": alert,
        "target": target,
        "target_verbose": channel["target_verbose"],
        "guard_error": guard_error,
        "index_url": index_url,
        "next": redirect_url,
    }
    return render(request, "cap/republish_event_confirm.html", context)


@login_required
def republish_mqtt_event(request, event_id):
    return _handle_republish(request, MQTT_CHANNEL, event_id)


@login_required
def republish_webhook_event(request, event_id):
    return _handle_republish(request, WEBHOOK_CHANNEL, event_id)


def _build_dissemination_groups(alert, channel, next_url):
    """Groups an alert's events for a channel by target, newest-first, with a
    per-target republish URL (rooting handled by the republish view)."""
    target_attr = channel["target_attr"]
    events = (
        getattr(alert, channel["events_related_name"])
        .select_related(target_attr, "source_event")
        .all()
    )
    
    groups = {}
    for event in events:  # model Meta orders by -created
        target = getattr(event, target_attr)
        group = groups.get(target.pk)
        if group is None:
            republish_url = "%s?next=%s" % (
                reverse(channel["republish_url_name"], args=[event.pk]),
                quote(next_url, safe=""),
            )
            group = {
                "target": target,
                "latest": event,
                "attempts": [],
                "republish_url": republish_url,
            }
            groups[target.pk] = group
        group["attempts"].append(event)
    
    return list(groups.values())


@login_required
def disseminations_view(request, alert_id):
    from .models import CapAlertPage
    
    if not request.user.has_perm("cap.can_view_alerts_menu"):
        raise PermissionDenied
    
    alert = get_object_or_404(CapAlertPage, id=alert_id)
    
    # Site scoping: the alert must belong to the current request's site.
    current_site = Site.find_for_request(request)
    if not current_site or alert.get_site() != current_site:
        raise Http404("Alert not found for this site")
    
    next_url = reverse("cap_disseminations", args=[alert.id])
    
    context = {
        "alert": alert,
        "mqtt_groups": _build_dissemination_groups(alert, MQTT_CHANNEL, next_url),
        "webhook_groups": _build_dissemination_groups(alert, WEBHOOK_CHANNEL, next_url),
        "can_republish": alert.permissions_for_user(request.user).can_publish(),
        "alerts_index_url": AdminURLHelper(CapAlertPage).get_action_url("index"),
    }
    return render(request, "cap/disseminations.html", context)
