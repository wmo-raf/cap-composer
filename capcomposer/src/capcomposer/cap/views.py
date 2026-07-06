import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.syndication.views import Feed
from django.core.validators import validate_email
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.feedgenerator import rfc2822_date
from django.utils.translation import gettext as _
from django.utils.xmlutils import SimplerXMLGenerator
from wagtail.admin import messages
from wagtail.admin.views.pages.create import CreateView
from wagtail.api.v2.utils import get_full_url
from wagtail.blocks import StreamValue
from wagtail_modeladmin.helpers import AdminURLHelper
import markdown

from capcomposer.capeditor.constants import SEVERITY_MAPPING
from capcomposer.capeditor.models import CapSetting
from capcomposer.capeditor.utils import get_event_info
from .cache import wagcache
from .models import (
    CapAlertPage,
    CapAlertListPage,
    OtherCAPSettings,
)
from .statistics import _get_filtered_queryset, get_alert_statistics, export_alerts_csv
from .utils import get_full_url_by_site, create_cap_alert_multi_media, send_private_alert_email
from .utils import (
    serialize_and_sign_cap_alert,
    get_currently_active_alerts,
    get_all_published_alerts
)


class CustomCAPFeed(Rss201rev2Feed):
    content_type = 'application/xml'
    
    def __init__(self, *args, **kwargs):
        self.cap_setting = kwargs.pop("cap_setting")
        
        self.cap_feed_stylesheet_full_url = get_full_url_by_site(self.cap_setting.site, reverse("cap_feed_stylesheet"))
        
        super().__init__(*args, **kwargs)
    
    def write(self, outfile, encoding):
        handler = SimplerXMLGenerator(outfile, encoding, short_empty_elements=True)
        handler.startDocument()
        
        # add stylesheet
        handler.processingInstruction('xml-stylesheet', f'type="text/xsl" href="{self.cap_feed_stylesheet_full_url}"')
        
        handler.startElement("rss", self.rss_attributes())
        handler.startElement("channel", self.root_attributes())
        self.add_root_elements(handler)
        self.write_items(handler)
        self.endChannelElement(handler)
        handler.endElement("rss")
    
    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        pubDate = rfc2822_date(self.latest_post_date())
        handler.addQuickElement('pubDate', pubDate)
        
        site = self.cap_setting.site
        
        logo = self.cap_setting.logo
        sender_name = self.cap_setting.sender_name
        
        if logo:
            url = logo.get_rendition('original').url
            url = site.root_url + url
            
            if url:
                # add logo image
                handler.startElement('image', {})
                handler.addQuickElement('url', url)
                
                if sender_name:
                    handler.addQuickElement('title', sender_name)
                
                if self.feed.get('link'):
                    handler.addQuickElement('link', site.root_url)
                
                handler.endElement('image')


class AlertListFeed(Feed):
    feed_copyright = "public domain"
    language = "en"
    
    feed_type = CustomCAPFeed
    
    def __call__(self, request, *args, **kwargs):
        self.cap_setting = CapSetting.for_request(request)
        return super().__call__(request, *args, **kwargs)
    
    def link(self):
        path = reverse("cap_alert_feed")
        full_url = get_full_url_by_site(self.cap_setting.site, path)
        return full_url
    
    def title(self):
        title = _("Latest alerts")
        if self.cap_setting.sender_name:
            title = _("Latest alerts from %(sender_name)s") % {"sender_name": self.cap_setting.sender_name}
        return title
    
    def description(self):
        description = _("Latest alerts")
        if self.cap_setting.sender_name:
            description = _("Latest alerts from %(sender_name)s") % {"sender_name": self.cap_setting.sender_name}
        return description
    
    def items(self):
        num_of_latest_alerts_in_feed = self.cap_setting.num_of_latest_alerts_in_feed
        site = self.cap_setting.site
        
        # get latest alerts, limit to num_of_latest_alerts_in_feed
        alerts = get_all_published_alerts()
        
        if site.root_page.specific_class == CapAlertListPage:
            alerts = alerts.child_of(site.root_page)
        
        alerts = alerts[:num_of_latest_alerts_in_feed]
        
        return alerts
    
    def item_title(self, item):
        return item.title
    
    def item_link(self, item):
        path = reverse("cap_alert_xml", args=[item.guid])
        full_url = get_full_url_by_site(self.cap_setting.site, path)
        return full_url
    
    def item_description(self, item):
        return item.info[0].value.get('description')
    
    def item_pubdate(self, item):
        return item.sent
    
    def item_enclosures(self, item):
        return super().item_enclosures(item)
    
    def item_guid(self, item):
        return item.identifier
    
    def item_author_name(self, item):
        if self.cap_setting.sender_name:
            return self.cap_setting.sender_name
        return None
    
    def item_author_email(self, item):
        if self.cap_setting.sender:
            try:
                # validate if sender is email address
                validate_email(self.cap_setting.sender)
                return self.cap_setting.sender
            except Exception:
                pass
        return None
    
    def item_categories(self, item):
        categories = item.info[0].value.get('category')
        
        if isinstance(categories, str):
            categories = [categories]
        
        return categories
    
    def feed_extra_kwargs(self, obj):
        return {
            "cap_setting": self.cap_setting
        }


def get_cap_xml(request, guid):
    alert = get_object_or_404(CapAlertPage, guid=guid)
    xml = wagcache.get(f"cap_alert_xml_{guid}")
    
    if not xml:
        xml, signed = serialize_and_sign_cap_alert(alert, request)
        xml = xml.decode("utf-8")
        
        if signed:
            # cache signed alerts for 5 days
            wagcache.set(f"cap_alert_xml_{guid}", xml, 60 * 60 * 24 * 5)
    
    return HttpResponse(xml, content_type="application/xml")


def get_cap_feed_stylesheet(request):
    stylesheet = wagcache.get("cap_feed_stylesheet")
    
    if not stylesheet:
        stylesheet = render_to_string("cap/cap-feed-stylesheet.html").strip()
        # cache for 5 days
        wagcache.set("cap_feed_stylesheet", stylesheet, 60 * 60 * 24 * 5)
    
    return HttpResponse(stylesheet, content_type="application/xml")

def get_cap_alert_stylesheet(request):
    context = {}
    cap_settings = CapSetting.for_request(request)
    if cap_settings.logo:
        context.update({
            "logo": cap_settings.logo,
            "sender_name": cap_settings.sender_name
        })
    
    stylesheet = wagcache.get("cap_alert_stylesheet")
    
    if not stylesheet:
        stylesheet = render_to_string("cap/cap-alert-stylesheet.html", context=context).strip()
        # cache for 5 days
        wagcache.set("cap_alert_stylesheet", stylesheet, 60 * 60 * 24 * 5)
    
    return HttpResponse(stylesheet, content_type="application/xml")


def cap_geojson(request):
    active_alerts = get_currently_active_alerts()
    
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for active_alert in active_alerts:
        features = active_alert.get_geojson_features(request)
        if features:
            geojson["features"].extend(features)
    
    return JsonResponse(geojson)


def get_home_map_alerts(request):
    alerts = get_currently_active_alerts()
    active_alert_infos = []
    geojson = {"type": "FeatureCollection", "features": []}
    
    cap_settings = OtherCAPSettings.for_request(request)
    default_alert_display_language = cap_settings.default_alert_display_language
    
    for alert in alerts:
        # take the first info
        info = alert.info[0]
        
        if default_alert_display_language and len(alert.info) > 1:
            for info_item in alert.info:
                info_lang = info_item.value.get("language")
                if info_lang == default_alert_display_language.code or info_lang.startswith(
                        default_alert_display_language.code):
                    info = info_item
                    break
        
        start_time = info.value.get("effective") or alert.sent
        
        if timezone.localtime() > start_time:
            status = "Ongoing"
        else:
            status = "Expected"
        
        area_desc = [area.get("areaDesc") for area in info.value.area]
        area_desc = ",".join(area_desc)
        
        event = info.value.get('event')
        
        event_info = get_event_info(event, request=request)
        
        event_icon = event_info.get("icon")
        
        alert_info = {
            "status": status,
            "url": alert.url,
            "event": event,
            "area_desc": area_desc,
            "event_icon": event_icon,
            "severity": SEVERITY_MAPPING[info.value.get("severity")],
            "expires": info.value.get("expires"),
            "language": info.value.get("language"),
            "properties": {
                "headline": info.value.get("headline"),
                "sent": alert.sent,
            }
        }
        
        active_alert_infos.append(alert_info)
        
        if info.value.features:
            for feature in info.value.features:
                geojson["features"].append(feature)
    context = {
        'has_alerts': len(active_alert_infos) > 0,
        'active_alert_info': active_alert_infos,
        'geojson': json.dumps(geojson)
    }
    
    return render(request, "home/section/home_map_alerts_include.html", context)


def get_latest_active_alert(request):
    other_cap_settings = OtherCAPSettings.for_request(request)
    active_alert_style = other_cap_settings.active_alert_style or "nav_left"
    default_alert_display_language = other_cap_settings.default_alert_display_language
    
    alerts = get_currently_active_alerts()
    active_alert_infos = []
    
    context = {}
    
    for alert in alerts:
        default_alert_info = alert.infos[0]
        
        if default_alert_display_language and len(alert.info) > 1:
            for info_item in alert.infos:
                info_lang = info_item.get("info").value.get("language")
                if info_lang == default_alert_display_language.code or info_lang.startswith(
                        default_alert_display_language.code):
                    default_alert_info = info_item
                    break
        
        default_alert_info.update({"title": alert.title, })
        active_alert_infos.append(default_alert_info)
    
    if len(active_alert_infos) == 0:
        context.update({
            'latest_active_alert': None
        })
    else:
        context.update({
            'latest_active_alert': active_alert_infos[0],
            'alert_style': active_alert_style
        })
    
    if active_alert_style == "nav_left":
        return render(request, "cap/widgets/nav_left_alert.html", context)
    
    if active_alert_style == "nav_top":
        return render(request, "cap/widgets/nav_top_alert.html", context)
    
    return render(request, "cap/widgets/nav_left_alert.html", context)


def create_cap_png_pdf(request, alert_id):
    """
    Create CAP alert PNG and PDF
    """
    alert = get_object_or_404(CapAlertPage, id=alert_id)
    
    # delete previous pdf preview if exists
    if alert.alert_pdf_preview:
        alert.alert_pdf_preview.delete()
    
    if alert.search_image:
        alert.search_image.delete()
    
    if alert.alert_area_map_image:
        alert.alert_area_map_image.delete()
    
    try:
        create_cap_alert_multi_media(alert.pk, clear_cache_on_success=True)
        messages.success(request, _("CAP Alert PNG and PDF created successfully."))
    except Exception as e:
        messages.error(request, _("Failed to create CAP Alert PNG and PDF."))
        messages.error(request, str(e))
    
    cap_index_url = AdminURLHelper(alert).get_action_url("index")
    return redirect(cap_index_url)

def send_private_alert_email_view(request, alert_id):
    """
    Send private alert email
    """
    alert = get_object_or_404(CapAlertPage, id=alert_id)
    
    try:
        send_private_alert_email(alert_id)
        messages.success(request, _("Private alert email sent successfully."))
    except Exception as e:
        messages.error(request, _("Failed to send private alert email."))
        messages.error(request, str(e))
    
    cap_index_url = AdminURLHelper(alert).get_action_url("index")
    return redirect(cap_index_url)


def third_party_integration(request):
    """
    A simple page to show third party integration options
    """
    cap_setting = CapSetting.for_request(request)

    cap_rss_feed_url = get_full_url(request, reverse("cap_alert_feed"))

    md_context = {
        "sender_name": cap_setting.sender_name,
        "feed_url": cap_rss_feed_url,
    }

    md = markdown.Markdown(extensions=["fenced_code", "codehilite"])

    md_content = render_to_string("cap/third_party_integration_md_content.md", md_context)

    md_content = md.convert(md_content)

    context = {
        **md_context,
        "md_content": md_content,
    }

    return render(request, "cap/third_party_integration.html", context)


@login_required
def cap_statistics_view(request):
    """Render the CAP alert statistics admin page."""
    queryset = _get_filtered_queryset(request)
    stats = get_alert_statistics(queryset)

    try:
        admin_list_url = AdminURLHelper(CapAlertPage).get_action_url("index")
    except Exception:
        admin_list_url = "/admin/"

    trend = stats["monthly_trend"]
    severity_colors_list = [stats["severity_colors"].get(k, "#ccc") for k in stats["by_severity"]]
    status_colors_list = [stats["status_colors"].get(k, "#ccc") for k in stats["by_status"]]

    context = {
        "stats": stats,
        "admin_list_url": admin_list_url,
        "start_date": request.GET.get("start_date", ""),
        "end_date": request.GET.get("end_date", ""),
        "selected_severities": request.GET.getlist("severity"),
        "severity_choices": ["Extreme", "Severe", "Moderate", "Minor"],
        "export_csv_url": reverse("cap_statistics_export_csv"),
        "trend_labels_json": json.dumps([row["label"] for row in trend]),
        "trend_data_json": json.dumps([row["count"] for row in trend]),
        "severity_labels_json": json.dumps(list(stats["by_severity"].keys())),
        "severity_data_json": json.dumps(list(stats["by_severity"].values())),
        "severity_colors_json": json.dumps(severity_colors_list),
        "urgency_labels_json": json.dumps(list(stats["by_urgency"].keys())),
        "urgency_data_json": json.dumps(list(stats["by_urgency"].values())),
        "certainty_labels_json": json.dumps(list(stats["by_certainty"].keys())),
        "certainty_data_json": json.dumps(list(stats["by_certainty"].values())),
        "status_labels_json": json.dumps(list(stats["by_status"].keys())),
        "status_data_json": json.dumps(list(stats["by_status"].values())),
        "status_colors_json": json.dumps(status_colors_list),
        "event_labels_json": json.dumps(list(stats["by_event"].keys())),
        "event_data_json": json.dumps(list(stats["by_event"].values())),
    }

    return render(request, "cap/statistics.html", context)


@login_required
def cap_statistics_api(request):
    """Return statistics as JSON, respecting the same query-param filters."""
    queryset = _get_filtered_queryset(request)
    stats = get_alert_statistics(queryset)
    return JsonResponse(stats, safe=False)


@login_required
def cap_statistics_export_csv(request):
    """Stream a CSV of the filtered alerts."""
    queryset = _get_filtered_queryset(request)
    csv_content = export_alerts_csv(queryset)

    response = HttpResponse(csv_content, content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="cap_alerts_statistics.csv"'
    return response


def _extract_polygon_geometry(geojson):
    """
    Return the first Polygon/MultiPolygon geometry found in a GeoJSON geometry,
    Feature or FeatureCollection, or None if none is found.
    """
    if not isinstance(geojson, dict):
        return None

    geojson_type = geojson.get("type")

    if geojson_type == "FeatureCollection":
        for feature in geojson.get("features") or []:
            geometry = _extract_polygon_geometry(feature)
            if geometry is not None:
                return geometry
        return None

    if geojson_type == "Feature":
        return _extract_polygon_geometry(geojson.get("geometry"))

    if geojson_type in ("Polygon", "MultiPolygon"):
        return geojson

    return None


def _build_area_info_blocks(request):
    """
    Build the ``info`` StreamField raw value with a single Alert Information block
    whose area is pre-filled from the ``geometry`` parameter, or None if no valid
    Polygon/MultiPolygon geometry is provided.

    The geometry is read from POST (the MapViewer submits it as a form body to
    avoid GET URL length limits) with a GET fallback for manual testing.
    """
    data = request.POST if request.method == "POST" else request.GET

    geometry_param = data.get("geometry")
    if not geometry_param:
        return None

    try:
        geojson = json.loads(geometry_param)
    except (ValueError, TypeError):
        return None

    geometry = _extract_polygon_geometry(geojson)
    if geometry is None:
        return None

    area_desc = (data.get("areaDesc") or "").strip()

    return [
        {
            "type": "alert_info",
            "value": {
                "area": [
                    {
                        "type": "polygon_block",
                        "value": {
                            "areaDesc": area_desc,
                            "polygon": json.dumps(geometry),
                        },
                    }
                ],
            },
        }
    ]


class CreateAlertFromGeometryView(CreateView):
    """
    Wagtail page CreateView that opens the standard 'add CAP alert' editor with the
    Alert Information area pre-filled from a GeoJSON geometry.

    The MapViewer submits the geometry via POST (a hidden form targeting a new
    tab) to avoid GET URL length limits; a GET fallback is kept for manual
    testing. In both cases nothing is written to the database — POST here only
    re-renders the prefilled add form, it does NOT run the CreateView create
    logic. Saving/publishing happens through the normal Wagtail add page flow
    (the rendered form posts to ``wagtailadmin_pages:add`` with its own CSRF
    token), so all validation and the usual field prefills apply as normal.
    """

    def _prefilled_form_response(self, request):
        info_blocks = _build_area_info_blocks(request)
        if info_blocks:
            self.page.info = StreamValue(
                self.page.info.stream_block, info_blocks, is_lazy=True
            )
        return super().get(request)

    def get(self, request):
        return self._prefilled_form_response(request)

    def post(self, request):
        # Render the prefilled form; deliberately NOT super().post() (no create).
        return self._prefilled_form_response(request)


@csrf_exempt
@login_required
def create_alert_from_geometry(request):
    """
    Entry point used by the MapViewer 'Create CAP alert' button. Resolves the CAP
    alert list page and renders the pre-filled add form via
    :class:`CreateAlertFromGeometryView`. Permissions are enforced by the underlying
    Wagtail CreateView (``can_add_subpage``).

    The geometry is submitted as the ``geometry`` form field (POST body, URL-encoded
    GeoJSON) so large polygons don't hit GET URL length limits; a GET ``geometry``
    query param is still accepted for manual testing. A bare geometry, a Feature or a
    FeatureCollection is accepted. An optional ``areaDesc`` field is used as the area
    description.

    ``csrf_exempt`` is safe here: this view only renders the prefilled add form and
    writes nothing to the database (``@login_required`` still applies), while the
    actual page creation posts to the CSRF-protected ``wagtailadmin_pages:add``.
    """
    cap_list_page = CapAlertListPage.objects.live().first()

    if not cap_list_page:
        return HttpResponseBadRequest(
            _("No CAP alert list page found. Please create one before adding alerts.")
        )

    return CreateAlertFromGeometryView.as_view()(
        request,
        content_type_app_name="cap",
        content_type_model_name="capalertpage",
        parent_page_id=cap_list_page.id,
    )
