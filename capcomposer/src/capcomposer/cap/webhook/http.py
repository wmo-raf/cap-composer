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
    
    if webhook.include_auth_header and webhook.header_value:
        headers["CAP-Webhook-Auth"] = webhook.header_value
    
    r = Request(
        method="POST",
        url=webhook.url,
        headers=headers,
        data=payload,
    )
    
    return r.prepare()
