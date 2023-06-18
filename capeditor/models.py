import uuid

from django.contrib.gis.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.forms import WagtailAdminPageForm
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.fields import StreamField
from wagtail.models import Page, Orderable, Site

from capeditor.blocks import AlertInfo


@register_setting
class CapSetting(BaseSiteSetting, ClusterableModel):
    sender = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Sender"))
    sender_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Sender Name"))
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Sender Contact"))

    panels = [
        FieldPanel("sender"),
        FieldPanel("sender_name"),
        FieldPanel("contact"),
    ]


def get_cap_setting():
    site = Site.objects.get(is_default_site=True)
    if site:
        return CapSetting.for_site(site)
    return None


def get_default_sender():
    cap_setting = get_cap_setting()
    if cap_setting and cap_setting.sender:
        return cap_setting.sender
    return None


class CapAlertPageForm(WagtailAdminPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cap_setting = get_cap_setting()

        default_sender_name = cap_setting.sender_name
        default_contact = cap_setting.contact

        if default_sender_name:
            info_field = self.fields.get("info")
            for block_type, block in info_field.block.child_blocks.items():
                if block_type == "alert_info":
                    field_name = "senderName"
                    sender_block = info_field.block.child_blocks[block_type].child_blocks[field_name]

                    label = sender_block.label or field_name
                    name = sender_block.name

                    info_field.block.child_blocks[block_type].child_blocks[field_name] = blocks.CharBlock(
                        default=default_sender_name, required=False)
                    info_field.block.child_blocks[block_type].child_blocks[field_name].name = name
                    info_field.block.child_blocks[block_type].child_blocks[field_name].label = label

        if default_contact:
            info_field = self.fields.get("info")
            for block_type, block in info_field.block.child_blocks.items():
                if block_type == "alert_info":
                    field_name = "contact"
                    contact_block = info_field.block.child_blocks[block_type].child_blocks[field_name]

                    label = contact_block.label or field_name
                    name = contact_block.name

                    info_field.block.child_blocks[block_type].child_blocks[field_name] = blocks.CharBlock(
                        default=default_contact, required=False)
                    info_field.block.child_blocks[block_type].child_blocks[field_name].name = name
                    info_field.block.child_blocks[block_type].child_blocks[field_name].label = label


class AbstractCapAlertPage(Page):
    base_form_class = CapAlertPageForm

    STATUS_CHOICES = (
        ("Draft", _("Draft - A preliminary template or draft, not actionable in its current form")),
        ("Actual", _("Actual - Actionable by all targeted recipients")),
        ("Test", _("Test - Technical testing only, all recipients disregard")),
        ("Exercise", _("Exercise - Actionable only by designated exercise participants; "
                       "exercise identifier SHOULD appear in note")),
        ("system", _("System - For messages that support alert network internal functions")),
    )

    MESSAGE_TYPE_CHOICES = (
        ('Alert', _("Alert - Initial information requiring attention by targeted recipients")),
        ('Update', _("Update - Updates and supersedes the earlier message(s) identified in referenced alerts")),
        ('Cancel', _("Cancel - Cancels the earlier message(s) identified in references")),
        ('Ack', _("Acknowledge - Acknowledges receipt and acceptance of the message(s) "
                  "identified in references field")),
        ('Error', _("Error -  Indicates rejection of the message(s) identified in references; "
                    "explanation SHOULD appear in note field")),
    )

    SCOPE_CHOICES = (
        ('Public', _("Public - For general dissemination to unrestricted audiences")),
        ('Restricted', _("Restricted - For dissemination only to users with a known operational "
                         "requirement as in the restriction field")),
        ('Private', _("Private - For dissemination only to specified addresses"
                      " as in the addresses field in the alert")),
    )

    identifier = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name=_("Identifier"),
                                  help_text=_("Unique ID. Auto generated on creation."), )
    sender = models.EmailField(max_length=255, verbose_name=_("Sender"), default=get_default_sender,
                               help_text=_("Identifies the originator of an alert. "
                                           "This can be an email of the institution for example"))
    sent = models.DateTimeField(default=timezone.now, verbose_name=_("Sent"),
                                help_text=_("Time and date of origination of the alert"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, verbose_name=_("Status"),
                              help_text=_("The code denoting the appropriate handling of the alert"))
    msgType = models.CharField(max_length=100, choices=MESSAGE_TYPE_CHOICES, verbose_name=_("Message Type"),
                               help_text=_("The code denoting the nature of the alert message"))
    scope = models.CharField(max_length=100, choices=SCOPE_CHOICES, verbose_name=_("Scope"),
                             help_text=_("The code denoting the intended distribution of the alert message"))
    source = models.TextField(blank=True, null=True, verbose_name=_("Source"),
                              help_text=_("The text identifying the source of the alert message"))
    restriction = models.TextField(blank=True, null=True,
                                   help_text=_("The text describing the rule for limiting distribution of the "
                                               "restricted alert message. Used when scope value is Restricted"),
                                   verbose_name=_("Restriction"))
    code = models.CharField(max_length=100, blank=True, null=True,
                            help_text=_("The code denoting the special handling of the alert message"),
                            verbose_name=_("Code"))
    note = models.TextField(blank=True, null=True,
                            help_text=_("The text describing the purpose or significance of the alert message."
                                        "The message note is primarily intended for use with "
                                        "<status> 'Exercise' and <msgType> 'Error'"), verbose_name=_("Note"))
    info = StreamField([
        ("alert_info", AlertInfo(label="Alert Information"))
    ], use_json_field=True, blank=True, null=True, verbose_name="Alert Information")

    content_panels = [
        MultiFieldPanel([
            FieldPanel('sender'),
            FieldPanel('sent'),
            FieldPanel('status', ),
            FieldPanel('msgType', classname="message"),
            FieldPanel('note', classname='note'),
            FieldPanel('scope'),
            FieldPanel('restriction', classname="restriction"),
        ], heading=_("Alert Identification")),
        FieldPanel("info")
    ]

# class AlertAddress(Orderable):
#     alert = ParentalKey('Alert', related_name="addresses", verbose_name=_("Alert"))
#     name = models.TextField(help_text=_("Name of the recipient"))
#     address = models.EmailField(blank=True, null=True, help_text=_("Email"), verbose_name=_("Email address"))
#
#     def __str__(self):
#         return self.name
#
#
# class AlertReference(Orderable):
#     alert = ParentalKey('Alert', related_name='references', verbose_name=_("Alert"))
#     ref_alert = models.ForeignKey('Alert', blank=True, null=True, on_delete=models.PROTECT,
#                                   help_text=_("Earlier alert referenced by this alert"),
#                                   verbose_name=_("Reference Alert"))
#
#     def __str__(self):
#         return f'{self.ref_alert.sender},{self.ref_alert.identifier},{self.ref_alert.sent}'
#
#     @property
#     def reference(self):
#         return f'{self.ref_alert.sender},{self.ref_alert.identifier},{self.ref_alert.sent}'
#
#
# class AlertIncident(Orderable):
#     alert = ParentalKey('Alert', related_name='incidents', on_delete=models.CASCADE, verbose_name=_("Alert"))
#     title = models.CharField(max_length=255, help_text=_("Title of the incident referent of the alert"),
#                              verbose_name=_("Title"))
#     description = models.TextField(help_text=_("Description of the incident"), verbose_name=_("Description"))
#
#     def __str__(self):
#         return self.title

# class AlertInfo(ClusterableModel):
#     LANGUAGE_CHOICES = (
#         ('en', _("English")),
#     )
#
#     CATEGORY_CHOICES = (
#         ('Geo', _("Geophysical")),
#         ('Met', _("Meteorological")),
#         ('Safety', _("General emergency and public safety")),
#         ('Security', _("Law enforcement, military, homeland and local/private security")),
#         ('Rescue', _("Rescue and recovery")),
#         ('Fire', _("Fire suppression and rescue")),
#         ('Health', _("Medical and public health")),
#         ('Env', _("Pollution and other environmental")),
#         ('Transport', _("Public and private transportation")),
#         ('Infra', _("Utility, telecommunication, other non-transport infrastructure")),
#         ('Cbrne', _("Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack")),
#         ('Other', _("Other events")),
#     )
#
#     URGENCY_CHOICES = (
#         ('Immediate', _("Immediate - Responsive action SHOULD be taken immediately")),
#         ('Expected', _("Expected - Responsive action SHOULD be taken soon (within next hour)")),
#         ('Future', _("Future - Responsive action SHOULD be taken in the near future")),
#         ('Past', _("Past - Responsive action is no longer required")),
#         ('Unknown', _("Unknown - Urgency not known")),
#     )
#
#     SEVERITY_CHOICES = (
#         ('Extreme', _("Extreme - Extraordinary threat to life or property")),
#         ('Severe', _("Severe - Significant threat to life or property")),
#         ('Moderate', _("Moderate - Possible threat to life or property")),
#         ('Minor', _("Minor - Minimal to no known threat to life or property")),
#         ('Unknown', _("Unknown - Severity unknown")),
#     )
#
#     CERTAINTY_CHOICES = (
#         ('Observed', _("Observed - Determined to have occurred or to be ongoing")),
#         ('Likely', _("Likely - Likely (percentage > ~50%)")),
#         ('Possible', _("Possible - Possible but not likely (percentage <= ~50%)")),
#         ('Unlikely', _("Unlikely - Not expected to occur (percentage ~ 0)")),
#         ('Unknown', _("Unknown - Certainty unknown")),
#     )
#
#     alert = ParentalKey('Alert', related_name="alert_info", )
#
#     language = models.CharField(max_length=100, choices=LANGUAGE_CHOICES, default='en', blank=True, null=True,
#                                 help_text=_("The code denoting the language of the alert message"),
#                                 verbose_name=_("Language"))
#     category = models.CharField(max_length=100, default='Met',
#                                 choices=CATEGORY_CHOICES,
#                                 help_text=_("The code denoting the category of the subject event of the alert message"),
#                                 verbose_name=_("Category"))
#     event = models.CharField(max_length=100,
#                              help_text=_("The text denoting the type of the subject event of the alert message"),
#                              blank=True, null=True, verbose_name=_("Event"))
#     urgency = models.CharField(max_length=100,
#                                choices=URGENCY_CHOICES,
#                                verbose_name=_("Urgency"),
#                                help_text=_("The code denoting the urgency of the subject event of the alert message"),
#                                default="Immediate")
#     severity = models.CharField(max_length=100,
#                                 choices=SEVERITY_CHOICES,
#                                 verbose_name=_("Severity"),
#                                 help_text=_("The code denoting the severity of the subject event of the alert message"),
#                                 default="Extreme")
#     certainty = models.CharField(max_length=100,
#                                  choices=CERTAINTY_CHOICES,
#                                  verbose_name=_("Certainty"),
#                                  help_text=_(
#                                      "The code denoting the certainty of the subject event of the alert message"),
#                                  default="Likely")
#     audience = models.TextField(blank=True, null=True,
#                                 verbose_name=_("Audience"),
#                                 help_text=_("The text describing the intended audience of the alert message"))
#
#     effective = models.DateTimeField(blank=True, null=True,
#                                      verbose_name=_("Effective"),
#                                      help_text=_("The effective time of the information of the alert message"))
#     onset = models.DateTimeField(blank=True, null=True,
#                                  verbose_name=_("Onset"),
#                                  help_text=_("The expected time of the beginning of the subject event "
#                                              "of the alert message"))
#     expires = models.DateTimeField(blank=True, null=True,
#                                    verbose_name=_("Expires"),
#                                    help_text=_("The expiry time of the information of the alert message"))
#     headline = models.TextField(blank=True, null=True, verbose_name=_("Headline"),
#                                 help_text=_("The text headline of the alert message"))
#     description = models.TextField(blank=True, null=True, verbose_name=_("Description"),
#                                    help_text=_("The text describing the subject event of the alert message"))
#     instruction = models.TextField(blank=True, null=True, verbose_name=_("Instruction"),
#                                    help_text=_("The text describing the recommended action to be taken by "
#                                                "recipients of the alert message"))
#     web = models.URLField(blank=True, null=True, verbose_name=_("Web"),
#                           help_text=_("The identifier of the hyperlink associating "
#                                       "additional information with the alert message"))
#     contact = models.TextField(blank=True, null=True, verbose_name=_("Contact"),
#                                help_text=_("The text describing the contact for follow-up and "
#                                            "confirmation of the alert message"))
#
#     panels = [
#
#         MultiFieldPanel([
#             FieldRowPanel([
#                 FieldPanel('language'),
#                 FieldPanel('event'),
#
#             ]),
#             FieldPanel('category'),
#             FieldPanel('urgency'),
#             FieldPanel('severity'),
#             FieldPanel('certainty'),
#             InlinePanel('response_types', heading="Response Types ", label="Response Type"),
#             FieldPanel('audience'),
#             # FieldPanel('event_codes'),
#             FieldRowPanel([
#                 FieldPanel('effective'),
#                 FieldPanel('onset'),
#             ]),
#             FieldPanel('expires'),
#
#         ], heading=_("Alert Categorization (Category, Urgency, Severity, Certainity, Response & Dates)"),
#             classname="collapsed"),
#
#         MultiFieldPanel([
#             FieldPanel('headline'),
#             FieldPanel('description'),
#             FieldPanel('instruction'),
#
#             FieldRowPanel([
#                 FieldPanel('web'),
#                 FieldPanel('contact'),
#             ])
#         ], heading=_("Alert Delivery Message (Headline, Description, Intsructions, Contact & Website)"),
#             classname="collapsed"),
#
#         MultiFieldPanel([
#             InlinePanel('resources', heading=_("Alert Resources "), label=_("Resource")),
#         ], classname="collapsed"),
#
#         MultiFieldPanel([
#             InlinePanel('alert_areas', heading=_("Alert Areas "), label=_("Alert Area")),
#         ], classname="collapsed"),
#
#     ]
#
#     @property
#     def is_expired(self):
#         difference = (timezone.now() - self.expires).days
#         if difference >= 0:
#             return True
#         return False
#
#
# class AlertResponseType(Orderable):
#     RESPONSE_TYPE_CHOICES = (
#         ("Shelter", _("Shelter - Take shelter in place or per instruction")),
#         ("Evacuate", _("Evacuate - Relocate as instructed in the instruction")),
#         ("Prepare", _("Prepare - Relocate as instructed in the instruction")),
#         ("Execute", _("Execute - Execute a pre-planned activity identified in instruction")),
#         ("Avoid", _("Avoid - Avoid the subject event as per the instruction")),
#         ("Monitor", _("Monitor - Attend to information sources as described in instruction")),
#         ("Assess", _("Assess - Evaluate the information in this message - DONT USE FOR PUBLIC ALERTS")),
#         ("AllClear",
#          _("All Clear - The subject event no longer poses a threat or concern and any follow on action is described in instruction")),
#         ("None", _("No action recommended")),
#     )
#
#     alert = ParentalKey('AlertInfo', related_name='response_types', null=True)
#     response_type = models.CharField(max_length=100, choices=RESPONSE_TYPE_CHOICES, verbose_name=_("Response type"),
#                                      help_text=_("The code denoting the type of action recommended for the "
#                                                  "target audience"))
#
#     def __str__(self) -> str:
#         return self.response_type
#
#
# class AlertResource(Orderable):
#     alert_info = ParentalKey('AlertInfo', related_name='resources', null=True)
#     mimeType = models.CharField(max_length=100, blank=True, null=True,
#                                 help_text=_("Resource type whether is image, file etc"))
#     resourceDesc = models.TextField(help_text=_("The text describing the type and content of the resource file"))
#     file = models.ForeignKey(
#         'wagtaildocs.Document',
#         help_text=_("File, Document etc"),
#         verbose_name=_("File"),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name='+',
#     )
#     uri = models.URLField(blank=True, null=True, help_text=_("The identifier of the hyperlink for the resource file"),
#                           verbose_name=_('Link'))
#     derefUri = models.TextField(blank=True, null=True,
#                                 help_text=_("The base-64 encoded data content of the resource file"))
#     digest = models.TextField(blank=True, null=True,
#                               help_text=_("The code representing the digital digest ('hash') computed "
#                                           "from the resource file"))
#
#     size = models.IntegerField(null=True, blank=True)
#
#     panels = [
#         FieldPanel('resourceDesc'),
#         FieldPanel('file'),
#     ]
#
#     @property
#     def mime_type(self):
#         return None
#
#     def save(self, *args, **kwargs):
#         self.size = self.file.file.size
#         self.mimeType = self.file.content_type
#         self.uri = self.file.url
#         with open(self.file.file.path, 'rb') as file:
#             document_content = file.read()
#         self.digest = hashlib.sha256(document_content).hexdigest()
#
#         return super(AlertResource, self).save(*args, **kwargs)
#
#
# class AlertArea(ClusterableModel):
#     alert_info = ParentalKey('AlertInfo', related_name='alert_areas', null=True)
#     areaDesc = models.CharField(max_length=100,
#                                 help_text=_("The text describing the affected area of the alert message"),
#                                 verbose_name=_("Affected areas / Regions"), null=True)
#
#     area = models.PolygonField(
#         help_text=_("The paired values of points defining a polygon that delineates the affected "
#                     "area of the alert message"), verbose_name=_("Area"), null=True, srid=4326)
#
#     altitude = models.CharField(max_length=100,
#                                 blank=True,
#                                 null=True,
#                                 help_text=_(
#                                     "The specific or minimum altitude of the affected area of the alert message"),
#                                 verbose_name=_("Altitude"))
#     ceiling = models.CharField(max_length=100,
#                                blank=True,
#                                null=True,
#                                verbose_name=_("Ceiling"),
#                                help_text=_("The maximum altitude of the affected area of the alert message."
#                                            "MUST NOT be used except in combination with the altitude element. "))
#
#     panels = [
#         FieldPanel('areaDesc'),
#         FieldPanel('area', widget=BasemapPolygonWidget()),
#         InlinePanel('geocodes', label="Geocode", heading="Geocodes "),
#         FieldPanel('altitude'),
#         FieldPanel('ceiling'),
#     ]
#
#
# class AlertEventCode(Orderable):
#     alert_info = ParentalKey('AlertInfo', related_name='event_codes', null=True)
#     name = models.CharField(max_length=100, help_text=_("Name for the event code"), verbose_name=_("Name"))
#     value = models.CharField(max_length=255, help_text=_("Value of the event code"), verbose_name=_("Value"))
#
#
# class AlertGeocode(Orderable):
#     alert_info = ParentalKey('AlertArea', related_name='geocodes', null=True)
#     name = models.CharField(max_length=100, help_text=_("Name for the geocode"), verbose_name=_("Name"))
#     value = models.CharField(max_length=255, help_text=_("Value of the geocode"), verbose_name=_("Value"))
