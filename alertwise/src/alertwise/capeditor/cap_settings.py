import json

from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, InlinePanel, TabbedInterface, ObjectList
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.fields import StreamField
from wagtail.models import Orderable
from wagtailiconchooser.widgets import IconChooserWidget
from wagtailmodelchooser import register_model_chooser

from alertwise.capeditor.blocks import (
    ContactBlock
)
from alertwise.capeditor.forms.widgets import (
    HazardEventTypeWidget,
    MultiPolygonWidget,
    GeojsonFileLoaderWidget, EventCodeWidget
)


@register_setting
class CapSetting(BaseSiteSetting, ClusterableModel):
    sender = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Sender Email"),
                              help_text=_("Email of the sending institution"))
    sender_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Sender Name"),
                                   help_text=_("Name of the sending institution"))
    wmo_oid = models.CharField(max_length=255, blank=True, null=True,
                               verbose_name=_("WMO Register of Alerting Authorities OID"),
                               help_text=_("WMO Register of Alerting Authorities "
                                           "Object Identifier (OID) of the sending institution. "
                                           "This will be used to generate CAP messages identifiers"))
    
    logo = models.ForeignKey("wagtailimages.Image", null=True, blank=True, on_delete=models.SET_NULL, related_name="+",
                             verbose_name=_("Logo of the sending institution"))
    
    contacts = StreamField([
        ("contact", ContactBlock(label=_("Contact")))
    ], use_json_field=True, blank=True, null=True, verbose_name=_("Contact Details"),
        help_text=_("Contact for follow-up and confirmation of the alert message"))
    
    un_country_boundary_geojson = models.JSONField(blank=True, null=True, verbose_name=_("UN Country Boundary"),
                                                   help_text=_("GeoJSON file of the UN Country Boundary. Setting this"
                                                               " will enable the UN Country Boundary check in the alert"
                                                               "drawing tools"))
    num_of_latest_alerts_in_feed = models.PositiveIntegerField(default=5, validators=[
        MinValueValidator(1),
        MaxValueValidator(50),
    ], verbose_name=_("Number of latest Alerts to show in the XML CAP Feed"), help_text=_("Set a smaller number to "
                                                                                          "improve perfomance for aggregators"))
    
    class Meta:
        verbose_name = _("CAP Settings")
    
    edit_handler = TabbedInterface([
        ObjectList([
            FieldPanel("sender_name"),
            FieldPanel("sender"),
            FieldPanel("wmo_oid"),
            FieldPanel("logo"),
            FieldPanel("contacts"),
        ], heading=_("Sender Details")),
        ObjectList([
            InlinePanel("hazard_event_types", heading=_("Hazard Types"), label=_("Hazard Type"),
                        help_text=_("Hazards monitored by the institution")),
        ], heading=_("Hazard Types")),
        ObjectList([
            InlinePanel("predefined_alert_areas", heading=_("Predefined Alert Areas"), label=_("Area"),
                        help_text=_("Predefined areas for alerts")),
        ], heading=_("Predefined Areas"), classname="map-resize-trigger"),
        ObjectList([
            InlinePanel("alert_languages", heading=_("Allowed Alert Languages"), label=_("Language")),
        ], heading=_("Languages")),
        ObjectList([
            FieldPanel("un_country_boundary_geojson",
                       widget=GeojsonFileLoaderWidget(
                           attrs={"resize_trigger_selector": ".w-tabs__tab.map-resize-trigger"})),
        ], heading=_("UN Boundary"), classname="map-resize-trigger"),
        ObjectList([
            FieldPanel("num_of_latest_alerts_in_feed"),
        ], heading=_("Other Settings")),
    ])
    
    @property
    def contact_list(self):
        contacts = []
        for contact_block in self.contacts:
            contact = contact_block.value.get("contact")
            if contact:
                contacts.append(contact)
        return contacts
    
    @property
    def audience_list(self):
        audiences = []
        for audience_block in self.audience_types:
            audience = audience_block.value.get("audience")
            if audience:
                audiences.append(audience)
        return audiences


class HazardEventTypes(Orderable):
    CATEGORY_CHOICES = (
        ('Geo', _("Geophysical")),
        ('Met', _("Meteorological")),
        ('Safety', _("General emergency and public safety")),
        ('Security', _("Law enforcement, military, homeland and local/private security")),
        ('Rescue', _("Rescue and recovery")),
        ('Fire', _("Fire suppression and rescue")),
        ('Health', _("Medical and public health")),
        ('Env', _("Pollution and other environmental")),
        ('Transport', _("Public and private transportation")),
        ('Infra', _("Utility, telecommunication, other non-transport infrastructure")),
        ('CBRNE', _("Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack")),
        ('Other', _("Other events")),
    )
    
    setting = ParentalKey(CapSetting, on_delete=models.PROTECT, related_name="hazard_event_types")
    is_in_wmo_event_types_list = models.BooleanField(default=True,
                                                     verbose_name=_("Select from WMO list of Hazards Event Types"))
    event = models.CharField(max_length=35, verbose_name=_("Hazard"), help_text=_("Name of Hazard"))
    category = models.CharField(max_length=35, default="Met", verbose_name=_("Category"),
                                choices=CATEGORY_CHOICES,
                                help_text=_("Category of Hazard"))
    event_code = models.CharField(max_length=10, blank=True, null=True, verbose_name=_("Event Code"))
    icon = models.CharField(max_length=255, null=True, blank=True, verbose_name=_("Icon"), help_text=_("Matching icon"))
    
    panels = [
        FieldPanel("is_in_wmo_event_types_list"),
        FieldPanel("event", widget=HazardEventTypeWidget),
        FieldPanel("category"),
        FieldPanel("event_code", widget=EventCodeWidget),
        FieldPanel("icon", widget=IconChooserWidget),
    ]
    
    def clean(self):
        if self.event_code is None:
            raise ValidationError({
                "event_code": ValidationError(_("Event Code is required"), code="required")
            })
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["setting", "event"],
                name="unique_setting_event",
                violation_error_message=_("This event type already exists")
            ),
        ]
    
    def __str__(self):
        return self.event


class PredefinedAlertArea(Orderable):
    setting = ParentalKey(CapSetting, on_delete=models.PROTECT, related_name="predefined_alert_areas")
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=4326, verbose_name=_("Area"))
    
    class Meta:
        verbose_name = _("Predefined Area")
        verbose_name_plural = _("Predefined Areas")
    
    def __str__(self):
        return self.name
    
    @property
    def geojson(self):
        return json.loads(self.geom.geojson)
    
    panels = [
        FieldPanel("name"),
        FieldPanel("geom",
                   widget=MultiPolygonWidget(attrs={"resize_trigger_selector": ".w-tabs__tab.map-resize-trigger"})),
    ]


register_model_chooser(PredefinedAlertArea)


class AlertLanguage(Orderable):
    setting = ParentalKey(CapSetting, on_delete=models.PROTECT, related_name="alert_languages")
    code = models.CharField(max_length=10, verbose_name=_("Language Code"), help_text=_("ISO 639-1 language code"))
    name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Language Name"))
    
    panels = [
        FieldPanel("code"),
        FieldPanel("name"),
    ]
    
    def __str__(self):
        return self.code
    
    def save(self, *args, **kwargs):
        self.code = self.code.lower()
        super().save(*args, **kwargs)
