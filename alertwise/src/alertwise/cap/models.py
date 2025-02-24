import json
import logging

from alertwise.capeditor.cap_settings import CapSetting
from alertwise.capeditor.models import AbstractCapAlertPage, CapAlertPageForm
from django.conf import settings
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.template.defaultfilters import truncatechars
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, gettext
from shapely.geometry import shape
from shapely.ops import unary_union
from wagtail import blocks
from wagtail.admin.panels import FieldPanel
from wagtail.api.v2.utils import get_full_url
from wagtail.contrib.settings.models import BaseSiteSetting
from wagtail.contrib.settings.registry import register_setting
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Page
from wagtail.signals import page_published

from .external_feed.models import ExternalAlertFeed, ExternalAlertFeedEntry
from .mixins import MetadataPageMixin
from .mqtt.models import CAPAlertMQTTBroker, CAPAlertMQTTBrokerEvent
from .mqtt.publish import publish_cap_to_all_mqtt_brokers
from .permissions import CAPMenuPermission
from .utils import (
    get_cap_map_style,
    get_all_published_alerts,
    create_cap_alert_multi_media
)
from .webhook.models import CAPAlertWebhook, CAPAlertWebhookEvent
from .webhook.utils import fire_alert_webhooks

__all__ = [
    "CapAlertListPage",
    "CapAlertPage",
    "OtherCAPSettings",
    "CAPAlertWebhook",
    "CAPAlertWebhookEvent",
    "CAPAlertMQTTBroker",
    "CAPAlertMQTTBrokerEvent",
    "ExternalAlertFeed",
    "ExternalAlertFeedEntry",
    "CAPMenuPermission",
]

logger = logging.getLogger(__name__)

MAX_CAP_LIST_PAGE_COUNT = getattr(settings, "MAX_CAP_LIST_PAGE_COUNT", None)
CAP_LIST_PAGE_PARENT_PAGE_TYPES = getattr(settings, "CAP_LIST_PAGE_PARENT_PAGE_TYPES", None)


class CapAlertListPage(MetadataPageMixin, Page):
    template = "cap/alert_list.html"
    subpage_types = ["cap.CapAlertPage"]
    max_count = MAX_CAP_LIST_PAGE_COUNT
    
    parent_page_types = CAP_LIST_PAGE_PARENT_PAGE_TYPES
    
    heading = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("CAP Alerts Heading"))
    
    alerts_infos_per_page = models.PositiveIntegerField(default=10, validators=[
        MinValueValidator(6),
        MaxValueValidator(20),
    ], help_text=_("Number of alerts to show per page"))
    
    content_panels = Page.content_panels + [
        FieldPanel("heading"),
        FieldPanel("alerts_infos_per_page"),
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        cap_rss_feed_url = get_full_url(request, reverse("cap_alert_feed"))
        
        current_page = request.GET.get("page", 1)
        
        site = self.get_site()
        
        context.update({
            "cap_rss_feed_url": cap_rss_feed_url,
        })
        
        other_cap_settings = OtherCAPSettings.for_site(site)
        default_alert_display_language = other_cap_settings.default_alert_display_language
        
        queryset = get_all_published_alerts().child_of(self)
        
        paginator = Paginator(queryset, self.alerts_infos_per_page)
        
        try:
            page_obj = paginator.page(current_page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        
        alert_infos = []
        
        for alert in page_obj.object_list:
            infos = alert.infos
            default_info = infos[0]
            
            # try to get the info in the default language
            if default_alert_display_language and len(alert.info) > 1:
                for info_item in infos:
                    info_lang = info_item.get("info").value.get("language")
                    if default_info:
                        if info_lang == default_alert_display_language.code or info_lang.startswith(
                                default_alert_display_language.code):
                            default_info = info_item
                            break
            
            # take first alert by default
            alert_infos.append(default_info)
        
        alert_infos = sorted(alert_infos, key=lambda x: x.get("sent", {}), reverse=True)
        
        active_alerts = []
        past_alerts = []
        
        for alert in alert_infos:
            if alert.get("expired"):
                past_alerts.append(alert)
            else:
                active_alerts.append(alert)
        
        alerts_by_expiry = {
            "active_alerts": active_alerts,
            "past_alerts": past_alerts,
        }
        
        context.update({
            "alerts_by_expiry": alerts_by_expiry,
            "filters": self.get_filters(alert_infos),
            "pagination": page_obj,
        })
        
        return context
    
    @staticmethod
    def get_filters(alerts):
        filters = {
            "severity": {},
            "event_types": {}
        }
        
        for alert_info in alerts:
            severity = alert_info.get("severity")
            severity_val = severity.get("severity")
            
            event_type = gettext(alert_info.get("info", {}).value.get('event'))
            
            if filters["event_types"].get(event_type):
                count = filters["event_types"].get(event_type).get("count") + 1
                filters["event_types"].get(event_type).update({"count": count})
            else:
                filters["event_types"].update({event_type: {
                    "count": 1,
                    "label": event_type
                }})
            
            if filters["severity"].get(severity_val):
                count = filters["severity"].get(severity_val).get("count") + 1
                filters["severity"].get(severity_val).update({"count": count})
            else:
                filters["severity"].update({severity_val: {
                    "count": 1,
                    "label": severity.get("label")
                }})
        
        return filters


class CapPageForm(CapAlertPageForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        is_imported = False
        if self.instance.pk:
            if hasattr(self.instance, "external_feed_entry"):
                is_imported = True
        
        references_field = self.fields.get("references")
        if references_field:
            for block_type, block in references_field.block.child_blocks.items():
                if block_type == "reference":
                    field_name = "ref_alert"
                    ref_alert_block = references_field.block.child_blocks[block_type].child_blocks[field_name]
                    
                    label = ref_alert_block.label or field_name
                    name = ref_alert_block.name
                    help_text = ref_alert_block._help_text
                    
                    references_field.block.child_blocks[block_type].child_blocks[field_name] = blocks.PageChooserBlock(
                        page_type="cap.CapAlertPage",
                        help_text=help_text,
                    )
                    references_field.block.child_blocks[block_type].child_blocks[field_name].name = name
                    references_field.block.child_blocks[block_type].child_blocks[field_name].label = label
        
        if is_imported:
            info_field = self.fields.get("info")
            
            # remove max_num for alert_info block. Allow having multiple info for multiple languages
            info_field.block.meta.max_num = None
            block_counts = info_field.block.meta.block_counts
            block_counts.update({"alert_info": {**block_counts.get("alert_info"), "max_num": None}})
            
            event_choices = []
            for info in self.instance.info:
                event = info.value.get("event")
                if event:
                    event_choices.append((event, event))
            
            for block_type, block in info_field.block.child_blocks.items():
                if block_type == "alert_info":
                    field_name = "event"
                    info_field.block.child_blocks[block_type].child_blocks[field_name].field.choices = event_choices
    
    def clean(self):
        cleaned_data = super().clean()
        
        # validate dates
        sent = cleaned_data.get("sent")
        alert_infos = cleaned_data.get("info")
        if sent and alert_infos:
            for info in alert_infos:
                effective = info.value.get("effective")
                expires = info.value.get("expires")
                
                if effective and sent and effective < sent:
                    self.add_error('info', _("Effective date cannot be earlier than the alert sent date."))
                
                if expires and sent and expires < sent:
                    self.add_error('info', _("Expires date cannot be earlier than the alert sent date."))
        
        return cleaned_data
    
    def save(self, commit=True):
        if self.instance.info:
            info = self.instance.info[0]
            expires = info.value.get("expires")
            if expires:
                self.instance.expires = expires
        
        return super().save(commit=commit)


class CapAlertPage(MetadataPageMixin, AbstractCapAlertPage):
    base_form_class = CapPageForm
    
    template = "cap/alert_detail.html"
    
    parent_page_types = ["cap.CapAlertListPage"]
    subpage_types = []
    
    expires = models.DateTimeField(blank=True, null=True)
    
    alert_area_map_image = models.ForeignKey(
        get_image_model(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    alert_pdf_preview = models.ForeignKey(
        get_document_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
    )
    
    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels,
    ]
    
    class Meta:
        ordering = ["-sent"]
        verbose_name = _("CAP Alert")
    
    @property
    def display_title(self):
        title = self.draft_title or self.title
        sent = self.sent.strftime("%Y-%m-%d %H:%M")
        return f"{self.status} - {sent} - {title}"
    
    def __str__(self):
        return self.display_title
    
    @property
    def is_published_publicly(self):
        return self.live and self.status == "Actual" and self.scope == "Public"
    
    def get_admin_display_title(self):
        return self.display_title
    
    def get_meta_description(self):
        info = self.info[0]
        description = info.value.get("description")
        
        if description:
            description = truncatechars(description, 160)
        
        return description
    
    @cached_property
    def xml_link(self):
        return reverse("cap_alert_xml", args=(self.guid,))
    
    @property
    def reference_alerts(self):
        alerts = []
        
        if self.msgType == "Alert":
            return alerts
        
        for ref in self.references:
            alert_page = ref.value.get("ref_alert")
            if alert_page:
                alerts.append(alert_page.specific)
        
        # sort by date sent
        alerts = sorted(alerts, key=lambda x: x.sent)
        
        return alerts
    
    @property
    def mbgl_renderer_payload(self):
        features = self.get_geojson_features()
        shapely_polygons = [shape(feature["geometry"]) for feature in features]
        combined = unary_union(shapely_polygons)
        bounding_box = list(combined.bounds)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        style = get_cap_map_style(geojson)
        
        payload = {
            "width": 400,
            "height": 400,
            "padding": 6,
            "style": style,
            "bounds": bounding_box,
        }
        
        return json.dumps(payload, cls=DjangoJSONEncoder)
    
    def get_geojson_features(self, request=None):
        features = []
        
        for info_item in self.infos:
            info = info_item.get("info")
            if info.value.geojson:
                web = info_item.get("url")
                if request:
                    web = get_full_url(request, web)
                
                properties = {
                    "id": self.identifier,
                    "event": info_item.get("event"),
                    "headline": info.value.get("headline"),
                    "severity": info.value.get("severity"),
                    "urgency": info.value.get("urgency"),
                    "certainty": info.value.get("certainty"),
                    "severity_color": info_item.get("severity", {}).get("color"),
                    "sent": self.sent,
                    "onset": info.value.get("onset"),
                    "expires": info.value.get("expires"),
                    "web": web,
                    "description": info.value.get("description"),
                    "instruction": info.value.get("instruction")
                }
                
                info_features = info.value.features
                for feature in info_features:
                    feature["properties"].update(**properties)
                    feature["order"] = info_item.get("severity", {}).get("id", 0)
                    features.append(feature)
        
        features = sorted(features, key=lambda x: x.get("order"))
        return features
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        cap_setting = CapSetting.for_request(request)
        
        other_cap_settings = OtherCAPSettings.for_request(request)
        default_alert_display_language = other_cap_settings.default_alert_display_language
        
        infos = context.get("page", {}).infos
        
        infos = sorted(infos, key=lambda x: x.get("severity", {}).get("id"), reverse=True)
        
        if default_alert_display_language:
            def sort_key(info, default_language_code):
                language = info.get("info").value.get("language")
                return language == default_language_code or language.startswith(default_language_code)
            
            # sort default language first
            infos = sorted(infos, key=lambda x: sort_key(x, default_alert_display_language.code), reverse=True)
        
        context.update({
            "org_logo": cap_setting.logo,
            "sender_name": cap_setting.sender_name,
            "sender_contact": cap_setting.sender,
            "alerts_url": self.get_parent().get_full_url(),
            "show_languages": len(self.info) > 1,
            "sorted_infos": infos,
        })
        
        return context


@register_setting(name="other-cap-settings")
class OtherCAPSettings(BaseSiteSetting):
    ACTIVE_ALERT_STYLE_CHOICES = [
        ("nav_left", _("Left of the Navbar")),
        ("nav_top", _("Top of the Navbar")),
    ]
    
    active_alert_style = models.CharField(max_length=50, choices=ACTIVE_ALERT_STYLE_CHOICES, default="nav_left",
                                          verbose_name=_("Active Alert Style"),
                                          help_text=_("Choose the style of active alerts"))
    default_alert_display_language = models.ForeignKey("capeditor.AlertLanguage", null=True, blank=True,
                                                       on_delete=models.SET_NULL)
    
    panels = [
        FieldPanel("active_alert_style"),
        FieldPanel("default_alert_display_language"),
    ]
    
    class Meta:
        verbose_name = _("Other Settings")
        verbose_name_plural = _("Other Settings")


def on_publish_cap_alert(sender, **kwargs):
    instance = kwargs['instance']
    
    if instance.status == "Actual" and instance.scope == "Public":
        try:
            # publish cap alert to mqtt
            publish_cap_to_all_mqtt_brokers(instance.id)
        except Exception as e:
            logger.error(f"Error publishing cap alert to mqtt: {e}")
            pass
        
        # publish cap alert to webhook
        try:
            fire_alert_webhooks(instance.id)
        except Exception as e:
            logger.error(f"Error publishing cap alert to webhook: {e}")
    
    # create cap alert multimedia (PNG and PDF)
    try:
        # delete previous pdf preview if exists
        if instance.alert_pdf_preview:
            instance.alert_pdf_preview.delete()
        
        if instance.search_image:
            instance.search_image.delete()
        
        if instance.alert_area_map_image:
            instance.alert_area_map_image.delete()
        
        create_cap_alert_multi_media(instance.pk, clear_cache_on_success=True)
    except Exception as e:
        logger.error(f"Error creating cap alert multimedia: {e}")


page_published.connect(on_publish_cap_alert, sender=CapAlertPage)
