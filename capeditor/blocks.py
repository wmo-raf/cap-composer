from django.contrib.gis import forms
from django.contrib.gis.geos import Polygon, GEOSGeometry
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.blocks import FieldBlock
from wagtailiconchooser.blocks import IconChooserBlock

from .widgets import PolygonWidget


class PolygonFieldBlock(FieldBlock):
    def __init__(self, required=True, help_text=None, srid=4326, **kwargs):
        self.field_options = {
            "required": required,
            "help_text": help_text,
            "srid": srid
        }

        super().__init__(**kwargs)

    @cached_property
    def field(self):
        field_kwargs = {"widget": PolygonWidget()}
        field_kwargs.update(self.field_options)
        return forms.PolygonField(**field_kwargs)

    def value_from_form(self, value):
        if value:
            if isinstance(value, Polygon):
                value = value.json

            geom = GEOSGeometry(value)

            return geom.json

        return None


class AlertArea(blocks.StructBlock):
    areaDesc = blocks.TextBlock(label=_("Affected areas / Regions"),
                                help_text=_("The text describing the affected area of the alert message"))
    polygon = PolygonFieldBlock(label=_("Polygon"),
                                help_text=_("The paired values of points defining a polygon that delineates "
                                            "the affected area of the alert message"))
    altitude = blocks.CharBlock(max_length=100, required=False, label=_("Altitude"),
                                help_text=_("The specific or minimum altitude of the affected "
                                            "area of the alert message"))
    ceiling = blocks.CharBlock(max_length=100, required=False, label=_("Ceiling"),
                               help_text=_("The maximum altitude of the affected area of the alert message."
                                           "MUST NOT be used except in combination with the altitude element. "))


SENDER_NAME_HELP_TEXT = _("The human-readable name of the agency or authority issuing this alert.")
CONTACT_HELP_TEXT = _("The text describing the contact for follow-up and confirmation of the alert message")
EVENT_HELP_TEXT = _("The text denoting the type of the subject event of the alert message")


class AlertInfo(blocks.StructBlock):
    LANGUAGE_CHOICES = (
        ('en', _("English")),
    )

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
        ('Cbrne', _("Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack")),
        ('Other', _("Other events")),
    )

    URGENCY_CHOICES = (
        ('Immediate', _("Immediate - Responsive action SHOULD be taken immediately")),
        ('Expected', _("Expected - Responsive action SHOULD be taken soon (within next hour)")),
        ('Future', _("Future - Responsive action SHOULD be taken in the near future")),
        ('Past', _("Past - Responsive action is no longer required")),
        ('Unknown', _("Unknown - Urgency not known")),
    )

    SEVERITY_CHOICES = (
        ('Extreme', _("Extreme - Extraordinary threat to life or property")),
        ('Severe', _("Severe - Significant threat to life or property")),
        ('Moderate', _("Moderate - Possible threat to life or property")),
        ('Minor', _("Minor - Minimal to no known threat to life or property")),
        ('Unknown', _("Unknown - Severity unknown")),
    )

    CERTAINTY_CHOICES = (
        ('Observed', _("Observed - Determined to have occurred or to be ongoing")),
        ('Likely', _("Likely - Likely (percentage > ~50%)")),
        ('Possible', _("Possible - Possible but not likely (percentage <= ~50%)")),
        ('Unlikely', _("Unlikely - Not expected to occur (percentage ~ 0)")),
        ('Unknown', _("Unknown - Certainty unknown")),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES, default="en", required=False, label=_("Language"),
                                  help_text=_("The code denoting the language of the alert message"), )
    category = blocks.ChoiceBlock(choices=CATEGORY_CHOICES, default="Met", label=_("Category"),
                                  help_text=_("The code denoting the category of the subject"
                                              " event of the alert message"))
    event = blocks.CharBlock(max_length=255, label=_("Event"), help_text=EVENT_HELP_TEXT)
    urgency = blocks.ChoiceBlock(choices=URGENCY_CHOICES, label=_("Urgency"),
                                 help_text=_("The code denoting the urgency of the subject "
                                             "event of the alert message"))
    severity = blocks.ChoiceBlock(choices=SEVERITY_CHOICES, label=_("Severity"),
                                  help_text=_("The code denoting the severity of the subject "
                                              "event of the alert message"))
    certainty = blocks.ChoiceBlock(choices=CERTAINTY_CHOICES, label=_("Certainty"),
                                   help_text=_("The code denoting the certainty of the subject "
                                               "event of the alert message"))
    headline = blocks.CharBlock(max_length=160, required=False, label=_("Headline"),
                                help_text=_("The text headline of the alert message. "
                                            "Make it direct and actionable as possible while remaining short"))
    description = blocks.TextBlock(required=False, label=_("Description"),
                                   help_text=_(
                                       "The text describing the subject event of the alert message. "
                                       "An extended description of the hazard or event that occasioned this message"))
    instruction = blocks.TextBlock(required=False, label=_("Instruction"),
                                   help_text=_("The text describing the recommended action to be taken by "
                                               "recipients of the alert message"))
    effective = blocks.DateTimeBlock(required=False, label=_("Effective"),
                                     help_text=_("The effective time of the information of the alert message. "
                                                 "If not set, the sent date will be used"))
    onset = blocks.DateTimeBlock(required=False, label=_("Onset"),
                                 help_text=_("The expected time of the beginning of the subject event "
                                             "of the alert message"))
    expires = blocks.DateTimeBlock(required=False, label=_("Expires"),
                                   help_text=_("The expiry time of the information of the alert message. "
                                               "If not set, each recipient is free to set its own policy as to when the"
                                               " message is no longer in effect."))
    senderName = blocks.CharBlock(max_length=255, label=_("Sender name"), required=False,
                                  help_text=SENDER_NAME_HELP_TEXT)
    contact = blocks.CharBlock(max_length=255, required=False, label=_("Contact"), help_text=CONTACT_HELP_TEXT)
    audience = blocks.CharBlock(max_length=255, required=False, label=_("Audience"),
                                help_text=_("The text describing the intended audience of the alert message"))

    area = blocks.ListBlock(AlertArea(), min_num=1, label="Alert Areas")

    # web
    # contact


class HazardTypeBlock(blocks.StructBlock):
    hazard = blocks.CharBlock(max_length=255, label=_("Hazard"), help_text="Name of Hazard")
    icon = IconChooserBlock(required=False)


class AudienceTypeBlock(blocks.StructBlock):
    audience = blocks.CharBlock(max_length=255, label=_("Audience"), help_text="Intended audience")
