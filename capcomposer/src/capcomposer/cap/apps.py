import base64

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from signxml import SignatureMethod

CAP_SIGNATURE_METHOD = getattr(settings, "CAP_SIGNATURE_METHOD", SignatureMethod.RSA_SHA256)
CAP_MQTT_SECRET_KEY = getattr(settings, "CAP_MQTT_SECRET_KEY", None)


class CapConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'capcomposer.cap'
    
    def ready(self):
        if CAP_SIGNATURE_METHOD and not hasattr(SignatureMethod, CAP_SIGNATURE_METHOD):
            message = f"Invalid 'CAP_SIGNATURE_METHOD' setting '{CAP_SIGNATURE_METHOD}'. " \
                      f"Must be one of " \
                      f"{list(SignatureMethod.__members__.keys())}"
            raise ImproperlyConfigured(message)
        
        if CAP_MQTT_SECRET_KEY:
            try:
                base64.urlsafe_b64decode(CAP_MQTT_SECRET_KEY)
            except Exception as e:
                raise ImproperlyConfigured(f"CAP_MQTT_SECRET_KEY must be a base64 encoded string. {e}")
            
            if len(CAP_MQTT_SECRET_KEY) != 44:
                raise ImproperlyConfigured("CAP_MQTT_SECRET_KEY must be 44 characters long")
