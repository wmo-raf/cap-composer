import logging

from requests import Session
from requests.exceptions import RequestException

from capcomposer.cap.utils import (
    serialize_and_sign_cap_alert
)
from capcomposer.utils import get_object_or_none
from .http import prepare_request


def fire_alert_webhooks(cap_alert_id):
    from capcomposer.cap.models import CapAlertPage
    from .models import CAPAlertWebhook, CAPAlertWebhookEvent

    cap_alert = get_object_or_none(CapAlertPage, id=cap_alert_id)

    if not cap_alert:
        logging.warning(f"CAP Alert: {cap_alert_id} not found")
        return
    
    if not cap_alert.live:
        logging.warning(f"CAP Alert: {cap_alert_id} is not published")
        return
    
    if not cap_alert.status == "Actual" and not cap_alert.scope == "Public":
        logging.warning(f"CAP Alert: {cap_alert_id} is not Public")
        return

    site = cap_alert.get_site()
    if not site:
        logging.warning(f"CAP Alert: {cap_alert_id} has no associated site, skipping webhook fire")
        return

    webhooks = CAPAlertWebhook.objects.filter(active=True, site=site)

    if not webhooks:
        logging.warning("No active webhooks found")
        return

    alert_xml, signed = serialize_and_sign_cap_alert(cap_alert)

    for webhook in webhooks:
        # Each fire is recorded as its own attempt (new event row)
        event = CAPAlertWebhookEvent.objects.create(
            webhook=webhook,
            alert=cap_alert,
            status="PENDING",
        )
        fire_alert_webhook(webhook, alert_xml, event)


def refire_alert_webhook(event):
    """Re-sends a CAP alert to the webhook referenced by an existing
    (PENDING) event row. Used by the operator-triggered republish flow.

    The alert-level guards and concurrency checks are enforced by the
    republish view before this runs; here we just (re)serialize and send.
    Failures are recorded on the event but not re-raised.
    """
    alert = event.alert
    webhook = event.webhook

    alert_xml, signed = serialize_and_sign_cap_alert(alert)

    fire_alert_webhook(webhook, alert_xml, event, reraise=False)


def fire_alert_webhook(webhook, alert_xml, event, reraise=True):
    """Sends the CAP alert XML to a single webhook, recording the
    outcome on the supplied event row.

    Args:
        webhook (CAPAlertWebhook): The target webhook.
        alert_xml (bytes): The CAP alert XML bytes to be sent.
        event (CAPAlertWebhookEvent): The pre-created event row whose
        status is updated with the outcome of this attempt.
        reraise (bool): Whether to re-raise on failure (auto-publish
        path) or swallow it after recording (republish path).
    """
    req = prepare_request(webhook, alert_xml)

    try:
        Session().send(req).raise_for_status()
        event.status = "SUCCESS"
        event.save()
    except RequestException as ex:
        status_code = ex.response.status_code if ex.response is not None else None
        logging.warning(f"Webhook request failed {status_code=}")

        event.status = "FAILURE"
        event.retries += 1
        event.error = str(ex)
        event.save()

        if reraise:
            raise ex
