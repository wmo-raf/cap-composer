from datetime import datetime

from django.utils import timezone
from requests import Request


def prepare_request(webhook, payload):
    now = timezone.localtime()
    timestamp = int(datetime.timestamp(now))
    
    headers = {
        "Content-Type": "application/xml",
        "CAP-Webhook-Request-Timestamp": str(timestamp),
    }
    r = Request(
        method="POST",
        url=webhook.url,
        headers=headers,
        data=payload,
    )
    
    return r.prepare()
