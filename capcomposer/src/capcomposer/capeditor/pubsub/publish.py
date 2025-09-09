from django.conf import settings

from capcomposer.capeditor.pubsub.mqtt import MQTTPubSubClient
from capcomposer.capeditor.renderers import CapXMLRenderer
from capcomposer.capeditor.serializers import AlertSerializer

BROKER_URI = getattr(settings, "CAP_BROKER_URI", None)


def publish_cap_mqtt_message(cap_alert_page, topic, qos=1):
    if BROKER_URI:
        broker = {
            'url': BROKER_URI,
            'client_type': 'publisher'
        }
        
        # create mqtt client
        client = MQTTPubSubClient(broker)
        
        # serialize cap alert to xml
        data = AlertSerializer(cap_alert_page).data
        cap_xml = CapXMLRenderer().render(data)
        
        # publish message
        client.pub(topic, message=cap_xml, qos=qos)
