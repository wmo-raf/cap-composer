from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from .utils import encrypt_password

CAP_MQTT_SECRET_KEY = getattr(settings, "CAP_MQTT_SECRET_KEY", None)


class CAPAlertMQTTBroker(models.Model):
    # Broker Information
    name = models.CharField(max_length=255, verbose_name=_("Name"),
                            help_text=_("Provide a name to identify the broker"))
    host = models.CharField(max_length=255, verbose_name=_("Broker Host"),
                            help_text=_("Provide the broker host name or IP address"))
    port = models.PositiveIntegerField(verbose_name=_("Broker Port"), help_text=_("Provide the broker port number")
                                       )
    # Authentication
    username = models.CharField(max_length=255, verbose_name=_("Broker Username"))
    new_password = models.CharField(max_length=255, blank=True, verbose_name=_("Broker Password"),
                                    help_text=_("Enter a password. If a password already exists, it will be updated"), )
    password = models.CharField(max_length=255)
    
    # Checkbox for if the MQTT broker is a WIS2 node
    is_wis2box = models.BooleanField(default=False, verbose_name=_("Is WIS2Box Node"),
                                     help_text=_("Check this box if you are providing the broker details of "
                                                 "a wis2box."))
    topic = models.CharField(max_length=255, blank=True, verbose_name=_("Topic"),
                             help_text=_("Provide the MQTT topic to publish the CAP alerts."), )
    # WIS2Box Metadata
    wis2box_metadata_id = models.CharField(max_length=255, blank=True, verbose_name=_("Dataset ID"),
                                           help_text=_(
                                               "Provide the metadata ID for your dataset registered in the wis2box. "
                                               "If you do not have this, please create a dataset in the wis2box "
                                               "before proceeding."))
    active = models.BooleanField(default=True, verbose_name=_("Active"),
                                 help_text=_("Automatically publish CAP alerts to this broker"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    retry_on_failure = models.BooleanField(default=True, verbose_name=_("Retry on failure"))
    
    panels = [
        MultiFieldPanel([
            FieldPanel("name"),
            FieldPanel("host"),
            FieldPanel("port"),
        ], heading=_("Broker Information")),
        MultiFieldPanel([
            FieldPanel("username"),
            FieldPanel("new_password"),
        ], heading=_("Authentication")),
        FieldPanel("is_wis2box"),
        FieldPanel("wis2box_metadata_id"),
        FieldPanel("topic"),
        FieldPanel("active"),
    ]
    
    def clean(self):
        """This method checks the following:

        1. If the broker is a WIS2 node, the metadata ID is required.
        2. If the broker is not a WIS2 node, the topic is required.
        3. The CAP_MQTT_SECRET_KEY is required for encrypting passwords.
        """
        
        if self.is_wis2box and not self.wis2box_metadata_id:
            raise ValidationError({
                "wis2box_metadata_id": _("Dataset ID is required for a WIS2Box Broker")
            })
        
        if not self.is_wis2box and not self.topic:
            raise ValidationError({
                "topic": _("Topic is required")
            })
        
        if not CAP_MQTT_SECRET_KEY:
            raise ValidationError(
                _("Secret key for encrypting passwords is not set. "
                  "Please ensure the CAP_MQTT_SECRET_KEY is set "))
        
        if not self.password and not self.new_password:
            raise ValidationError({
                "new_password": _("Password is required if creating a new broker")
            })
    
    def save(self, *args, **kwargs):
        """This does the following:

        1. If a new password is provided, it is encrypted and saved as 'password'.
        2. The new password is reset to an empty string.
        3. Calls the parent save method.
        """
        if self.new_password != "":
            self.password = encrypt_password(self.new_password)
            self.new_password = ""
        
        if self.is_wis2box and self.wis2box_metadata_id:
            self.topic = "wis2box/cap/publication"
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ["-created"]
        verbose_name = _("MQTT Broker")
        verbose_name_plural = _("MQTT Brokers")
    
    def __str__(self):
        return f"{self.name} - {self.host}:{self.port}"


MQTT_STATES = [
    ("PENDING", _("Pending")),
    ("FAILURE", _("Failure")),
    ("SUCCESS", _("Success")),
]


class CAPAlertMQTTBrokerEvent(models.Model):
    broker = models.ForeignKey(CAPAlertMQTTBroker, on_delete=models.CASCADE, related_name="events")
    alert = models.ForeignKey("cap.CapAlertPage", on_delete=models.CASCADE, related_name="mqtt_broker_events")
    status = models.CharField(max_length=40, choices=MQTT_STATES, default="PENDING", verbose_name=_("Status"),
                              editable=False)
    retries = models.IntegerField(default=0, verbose_name=_("Retries"))
    error = models.TextField(blank=True, null=True, verbose_name=_("Last Error Message"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("MQTT Broker Event")
        verbose_name_plural = _("MQTT Broker Events")
    
    def __str__(self):
        return f"{self.broker.name} - {self.alert.title}"
