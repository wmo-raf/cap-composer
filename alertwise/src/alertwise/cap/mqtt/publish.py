import json
import logging
from base64 import b64encode

import paho.mqtt.publish as publish
from alertwise.utils import get_object_or_none
from django.conf import settings

from .models import CAPAlertMQTTBroker, CAPAlertMQTTBrokerEvent
from .utils import decrypt_password
from ..utils import serialize_and_sign_cap_alert

logger = logging.getLogger(__name__)

CAP_WIS2BOX_INTERNAL_TOPIC = getattr(settings, "CAP_WIS2BOX_INTERNAL_TOPIC", "wis2box/cap/publication")


def publish_cap_to_all_mqtt_brokers(cap_alert_id):
    from alertwise.cap.models import CapAlertPage
    
    """Automatically publishes the CAP alert to all MQTT brokers
    configured in the editor.

        cap_alert_id (int): The ID of the CAP alert, used to fetch
        the CAP alert instance from the database.
    """
    
    logging.info(
        f"Starting publish_cap_to_all_mqtt_brokers for CAP Alert ID: {cap_alert_id}")
    
    # Get all active brokers
    brokers = CAPAlertMQTTBroker.objects.filter(active=True)
    
    if not brokers:
        logging.warning("No MQTT brokers found")
        return
    
    # Get the cap alert data to be published
    cap_alert = get_object_or_none(CapAlertPage, id=cap_alert_id)
    logging.info(f"CAP Alert: {cap_alert} found")
    
    if not cap_alert:
        logging.warning(f"CAP Alert: {cap_alert_id} not found")
        return
    
    if not cap_alert.live:
        logging.warning(f"CAP Alert: {cap_alert_id} is not published")
        return
    
    if cap_alert.status != "Actual":
        logging.warning(f"CAP Alert: {cap_alert_id} is not actionable")
        return
    
    # Get the processed CAP alert XML
    alert_xml, signed = serialize_and_sign_cap_alert(cap_alert)
    
    if not signed:
        logging.warning(f"CAP Alert: {cap_alert_id} not signed")
        # Continue to publish anyway, the acceptance/rejection of non-signed
        # alerts should be handled on the receiving side (e.g. a wis2box)
    
    for broker in brokers:
        publish_cap_to_each_mqtt_broker(cap_alert, alert_xml, broker)


def publish_cap_to_each_mqtt_broker(alert, alert_xml, broker):
    """Formats the message for MQTT publishing and publishes it
    to a given broker.

    Args:
        alert (CapAlertPage): The CAP alert instance to obtain metadata.
        alert_xml (bytes): The CAP alert XML bytes to be published.
        broker (CAPALertMQTTBroker): The broker configured by the user,
        containing details such as the host, port, and authentication.

    Raises:
        ex: An exception if the Paho MQTT publishing step fails
        after all retries.
    """
    
    event = CAPAlertMQTTBrokerEvent.objects.filter(broker=broker, alert=alert).first()
    
    if not event:
        event = CAPAlertMQTTBrokerEvent.objects.create(broker=broker, alert=alert, status="PENDING")
    
    # Encode the CAP alert message in base64
    data = b64encode(alert_xml).decode()
    alert_dt = alert.sent.strftime("%Y%m%dT%H%M%S")
    # Create the filename
    filename = f"{alert.status}_{alert_dt}_{alert.slug}.xml"
    
    # Create the notification to be sent to the internal broker
    msg = {
        "data": data,
        "filename": filename
    }
    
    # If it is a WIS2 node, add the metadata ID
    if broker.is_wis2box:
        msg["metadata_id"] = broker.wis2box_metadata_id
    
    private_auth = {
        "username": broker.username,
        "password": decrypt_password(broker.password)
    }
    
    # Publish notification on internal broker,
    try:
        publish.single(
            topic=broker.topic,
            payload=json.dumps(msg),
            qos=1,
            retain=False,
            hostname=broker.host,
            port=int(broker.port),
            auth=private_auth,
        )
        event.status = "SUCCESS"
        logging.info(f"CAP Alert successfully published to MQTT broker: {broker.name}")
        event.save()
    except Exception as ex:
        logging.warning(
            f"CAP Alert MQTT Broker Event failed: {ex}",
            exc_info=True)
        event.status = "FAILURE"
        event.retries += 1
        event.error = str(ex)
        event.save()
