import logging

from alertwise.cap.utils import (
    serialize_and_sign_cap_alert
)
from alertwise.utils import get_object_or_none
from requests import Session
from requests.exceptions import RequestException

from .http import prepare_request


def fire_alert_webhooks(cap_alert_id):
    from alertwise.cap.models import CapAlertPage
    from .models import CAPAlertWebhook, CAPAlertWebhookEvent
    
    webhooks = CAPAlertWebhook.objects.filter(active=True)
    
    if not webhooks:
        logging.warning("No active webhooks found")
        return
    
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
    
    alert_xml, signed = serialize_and_sign_cap_alert(cap_alert)
    
    for webhook in webhooks:
        req = prepare_request(webhook, alert_xml)
        
        event = CAPAlertWebhookEvent.objects.filter(webhook=webhook, alert=cap_alert).first()
        
        if not event:
            event = CAPAlertWebhookEvent.objects.create(
                webhook=webhook,
                alert=cap_alert,
                status="PENDING",
            )
        
        try:
            Session().send(req).raise_for_status()
            event.status = "SUCCESS"
            event.save()
        except RequestException as ex:
            status_code = ex.response.status_code
            logging.warning(f"Webhook request failed {status_code=}")
            
            event.status = "FAILURE"
            event.retries += 1
            event.error = str(ex)
            event.save()
            
            raise ex
