import io
import json
import tempfile
from datetime import datetime
from urllib.parse import urlsplit

import pytz
import requests
import weasyprint
from alertwise.capeditor.models import CapSetting
from alertwise.capeditor.renderers import CapXMLRenderer
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_str
from lxml import etree
from pdf2image import convert_from_path
from wagtail.api.v2.utils import get_full_url
from wagtail.blocks import StreamValue
from wagtail.documents import get_document_model
from wagtail.images import get_image_model
from wagtail.models import Site
from wagtailcache.cache import clear_cache

from .constants import DEFAULT_STYLE, CAP_LAYERS
from .exceptions import CAPAlertImportError
from .sign import sign_cap_xml
from .weasyprint_utils import django_url_fetcher
from ..utils import get_object_or_none


def get_all_published_alerts():
    from .models import CapAlertPage
    return CapAlertPage.objects.all().live().filter(status="Actual", scope="Public").order_by('-sent')


def get_currently_active_alerts():
    current_time = timezone.localtime()
    return get_all_published_alerts().filter(expires__gte=current_time)


def create_cap_pdf_document(cap_alert, template_name):
    site = cap_alert.get_site()
    cap_settings = CapSetting.for_site(site)
    
    # TODO: handle case where logo is not set
    org_logo = cap_settings.logo
    
    infos = cap_alert.infos
    infos = sorted(infos, key=lambda x: x.get("severity", {}).get("id"), reverse=True)
    cap_alert.infos = infos
    
    context = {
        "org_logo": org_logo,
        "sender_name": cap_settings.sender_name,
        "sender_contact": cap_settings.sender,
        "alerts_url": cap_alert.get_parent().get_full_url().strip("/"),
        "page": cap_alert
    }
    
    html_string = render_to_string(template_name, context)
    
    html = weasyprint.HTML(string=html_string, url_fetcher=django_url_fetcher, base_url='file://')
    
    buffer = io.BytesIO()
    html.write_pdf(buffer)
    
    buff_val = buffer.getvalue()
    
    content_file = ContentFile(buff_val, f"{cap_alert.id}.pdf")
    
    document = get_document_model().objects.create(title=cap_alert.title, file=content_file)
    
    return document


def get_cap_map_style(geojson):
    style = DEFAULT_STYLE
    style["sources"].update({"cap_alert": {"type": "geojson", "data": geojson}})
    layers = CAP_LAYERS
    for layer in layers:
        layer_type = layer.get("type")
        layer["source"] = "cap_alert"
        
        if layer_type == "fill":
            layer["id"] = "cap_alert_fill"
        
        if layer_type == "line":
            layer["id"] = "cap_alert_line"
        
        if layer.get("filter"):
            del layer["filter"]
    
    style["layers"].extend(layers)
    
    return style


def create_cap_area_map_image(cap_alert):
    MBGL_RENDERER_URL = getattr(settings, "MBGL_RENDERER_URL", None)
    
    if not MBGL_RENDERER_URL:
        print("MBGL_RENDERER_URL is not set in settings")
        return None
    
    mbgl_payload = cap_alert.mbgl_renderer_payload
    
    headers = {'Content-type': 'application/json'}
    r = requests.post(MBGL_RENDERER_URL, data=mbgl_payload, headers=headers, stream=True)
    
    r.raise_for_status()
    
    file_id = cap_alert.last_published_at.strftime("%s")
    filename = f"{cap_alert.id}_{file_id}_map.png"
    
    sent = cap_alert.sent.strftime("%Y-%m-%d-%H-%M")
    image_title = f"{sent} - Alert Area Map"
    
    # create content file from response
    content_file = ContentFile(r.content, filename)
    area_image = get_image_model().objects.create(title=image_title, file=content_file)
    
    return area_image


def get_cap_settings():
    site = Site.objects.get(is_default_site=True)
    cap_settings = CapSetting.for_site(site)
    return cap_settings


def serialize_and_sign_cap_alert(alert, request=None):
    from .serializers import AlertSerializer
    
    data = AlertSerializer(alert, context={
        "request": request,
    }).data
    
    xml = CapXMLRenderer().render(data)
    xml_bytes = bytes(xml, encoding='utf-8')
    signed = False
    
    try:
        signed_xml = sign_cap_xml(xml_bytes)
        if signed_xml:
            xml = signed_xml
            signed = True
    except Exception as e:
        pass
    
    if signed:
        root = etree.fromstring(xml)
    else:
        root = etree.fromstring(xml_bytes)
    
    style_url = get_full_url(request, reverse("cap_alert_stylesheet"))
    
    tree = etree.ElementTree(root)
    pi = etree.ProcessingInstruction('xml-stylesheet', f'type="text/xsl" href="{style_url}"')
    tree.getroot().addprevious(pi)
    xml = etree.tostring(tree, xml_declaration=True, encoding='utf-8')
    
    return xml, signed


def get_cap_contact_list(request):
    cap_settings = CapSetting.for_request(request)
    contacts_list = cap_settings.contact_list
    return contacts_list


def get_cap_audience_list(request):
    cap_settings = CapSetting.for_request(request)
    audience_list = cap_settings.audience_list
    return audience_list


def create_cap_alert_multi_media(cap_alert_page_id, clear_cache_on_success=False):
    from .models import CapAlertPage
    
    try:
        cap_alert = get_object_or_none(CapAlertPage, id=cap_alert_page_id)
        
        if cap_alert:
            print("[CAP] Generating CAP Alert MultiMedia content for: ", cap_alert.title)
            # create alert area map image
            cap_alert_area_map_image = create_cap_area_map_image(cap_alert)
            
            if cap_alert_area_map_image:
                print("[CAP] 1. CAP Alert Area Map Image created for: ", cap_alert.title)
                cap_alert.alert_area_map_image = cap_alert_area_map_image
                cap_alert.save()
                
                # create_cap_pdf_document
                cap_preview_document = create_cap_pdf_document(cap_alert, template_name="cap/alert_detail_pdf.html")
                cap_alert.alert_pdf_preview = cap_preview_document
                cap_alert.save()
                
                print("[CAP] 2. CAP Alert PDF Document created for: ", cap_alert.title)
                
                file_id = cap_alert.last_published_at.strftime("%s")
                preview_image_filename = f"{cap_alert.id}_{file_id}_preview.jpg"
                
                sent = cap_alert.sent.strftime("%Y-%m-%d-%H-%M")
                preview_image_title = f"{sent} - Alert Preview"
                
                # get first page of pdf as image
                cap_preview_image = get_first_page_of_pdf_as_image(file_path=cap_preview_document.file.path,
                                                                   title=preview_image_title,
                                                                   file_name=preview_image_filename)
                
                print("[CAP] 3. CAP Alert Preview Image created for: ", cap_alert.title)
                
                if cap_preview_image:
                    cap_alert.search_image = cap_preview_image
                    cap_alert.save()
                
                print("[CAP] CAP Alert MultiMedia content saved for: ", cap_alert.title)
                
                if clear_cache_on_success:
                    clear_cache()
        else:
            print("[CAP] CAP Alert not found for ID: ", cap_alert_page_id)
    except Exception as e:
        print("[CAP] Error in create_cap_alert_multi_media: ", e)
        pass


def get_cap_contact_list_for_site(site):
    cap_settings = CapSetting.for_site(site)
    contacts_list = cap_settings.contact_list
    return contacts_list


def get_cap_audience_list_for_site(site):
    cap_settings = CapSetting.for_site(site)
    audience_list = cap_settings.audience_list
    return audience_list


def create_draft_alert_from_alert_data(alert_data, request=None, update_event_list=False, update_contact_list=False,
                                       submit_for_moderation=False):
    from .models import CapAlertPage, CapAlertListPage
    
    if request:
        cap_settings = CapSetting.for_request(request)
    else:
        site = Site.objects.get(is_default_site=True)
        cap_settings = CapSetting.for_site(site)
    
    base_data = {}
    
    # an alert page requires a title
    # here we use the headline of the first info block
    title = None
    
    if "sender" in alert_data:
        base_data["sender"] = alert_data["sender"]
    if "sent" in alert_data:
        sent = alert_data["sent"]
        # convert dates to local timezone
        sent = datetime.fromisoformat(sent).astimezone(pytz.utc)
        sent_local = sent.astimezone(timezone.get_current_timezone())
        base_data["sent"] = sent_local
    if "status" in alert_data:
        base_data["status"] = alert_data["status"]
    if "msgType" in alert_data:
        base_data["msgType"] = alert_data["msgType"]
    if "scope" in alert_data:
        base_data["scope"] = alert_data["scope"]
    if "restriction" in alert_data:
        base_data["restriction"] = alert_data["restriction"]
    if "note" in alert_data:
        base_data["note"] = alert_data["note"]
    
    info_blocks = []
    
    if "info" in alert_data:
        for info in alert_data.get("info"):
            info_base_data = {}
            
            if "language" in info:
                alert_language_code = info["language"]
                
                alert_languages = cap_settings.alert_languages.all()
                
                existing_alert_language = alert_languages.filter(code__iexact=alert_language_code).first()
                if existing_alert_language:
                    info_base_data["language"] = existing_alert_language.code
                else:
                    # create new alert language
                    alert_languages.create(setting=cap_settings, code=alert_language_code, name=alert_language_code)
                    info_base_data["language"] = alert_language_code
            
            if "category" in info:
                info_base_data["category"] = info["category"]
            if "event" in info:
                event = info["event"]
                if update_event_list:
                    hazard_event_types = cap_settings.hazard_event_types.all()
                    existing_hazard_event_type = hazard_event_types.filter(event__iexact=event).first()
                    if not existing_hazard_event_type:
                        hazard_event_types.create(setting=cap_settings, is_in_wmo_event_types_list=False, event=event,
                                                  icon="warning")
                
                info_base_data["event"] = event
            
            if "responseType" in info:
                response_types = info["responseType"]
                response_type_data = []
                for response_type in response_types:
                    response_type_data.append({"response_type": response_type})
                info_base_data["responseType"] = response_type_data
            
            if "urgency" in info:
                info_base_data["urgency"] = info["urgency"]
            if "severity" in info:
                info_base_data["severity"] = info["severity"]
            if "certainty" in info:
                info_base_data["certainty"] = info["certainty"]
            if "eventCode" in info:
                event_codes = info["eventCode"]
                event_code_data = []
                for event_code in event_codes:
                    event_code_data.append({"valueName": event_code["valueName"], "value": event_code["value"]})
                info_base_data["eventCode"] = event_code_data
            if "effective" in info:
                effective = info["effective"]
                effective = datetime.fromisoformat(effective).astimezone(pytz.utc)
                effective_local = effective.astimezone(timezone.get_current_timezone())
                info_base_data["effective"] = effective_local
            if "onset" in info:
                onset = info["onset"]
                onset = datetime.fromisoformat(onset).astimezone(pytz.utc)
                onset_local = onset.astimezone(timezone.get_current_timezone())
                info_base_data["onset"] = onset_local
            if "expires" in info:
                expires = info["expires"]
                expires = datetime.fromisoformat(expires).astimezone(pytz.utc)
                expires_local = expires.astimezone(timezone.get_current_timezone())
                info_base_data["expires"] = expires_local
            if "senderName" in info:
                info_base_data["senderName"] = info["senderName"]
            if "description" in info:
                info_base_data["description"] = info["description"]
            if "headline" in info or "event" in info:
                headline = info.get("headline") or info.get("event")
                info_base_data["headline"] = headline
                if not title:
                    title = headline
            
            if "description" in info:
                info_base_data["description"] = info["description"]
            if "instruction" in info:
                info_base_data["instruction"] = info["instruction"]
            if "contact" in info:
                contact = info["contact"]
                if update_contact_list:
                    if request:
                        contact_list = get_cap_contact_list(request)
                    else:
                        contact_list = get_cap_contact_list_for_site(cap_settings.site)
                    if contact not in contact_list:
                        cap_settings.contacts.append(("contact", {"contact": contact}))
                        cap_settings.save()
                
                info_base_data["contact"] = contact
            if "audience" in info:
                info_base_data["audience"] = info["audience"]
            
            if "parameter" in info:
                parameters = info["parameter"]
                parameter_data = []
                for parameter in parameters:
                    parameter_data.append({"valueName": parameter["valueName"], "value": parameter["value"]})
                info_base_data["parameter"] = parameter_data
            if "resource" in info:
                resources = info["resource"]
                resource_data = []
                for resource in resources:
                    if resource.get("uri") and resource.get("resourceDesc"):
                        resource_data.append({
                            "type": "external_resource",
                            "value": {
                                "external_url": resource["uri"],
                                "resourceDesc": resource["resourceDesc"]
                            }
                        })
                info_base_data["resource"] = resource_data
            
            areas_data = []
            if "area" in info:
                for area in info.get("area"):
                    area_data = {}
                    areaDesc = area.get("areaDesc")
                    
                    if "geocode" in area:
                        area_data["type"] = "geocode_block"
                        geocode = area.get("geocode")
                        geocode_data = {
                            "areaDesc": areaDesc,
                        }
                        if "valueName" in geocode:
                            geocode_data["valueName"] = geocode["valueName"]
                        if "value" in geocode:
                            geocode_data["value"] = geocode["value"]
                        
                        area_data["value"] = geocode_data
                    
                    if "polygon" in area:
                        area_data["type"] = "polygon_block"
                        polygon_data = {
                            "areaDesc": areaDesc,
                        }
                        geometry = area.get("geometry")
                        polygon_data["polygon"] = json.dumps(geometry)
                        
                        area_data["value"] = polygon_data
                    
                    if "circle" in area:
                        area_data["type"] = "circle_block"
                        circle_data = {
                            "areaDesc": areaDesc,
                        }
                        circle = area.get("circle")
                        # take the first circle for now
                        # TODO: handle multiple circles ? Investigate use case
                        circle_data["circle"] = circle[0]
                        area_data["value"] = circle_data
                    
                    areas_data.append(area_data)
            
            stream_item = {
                "type": "alert_info",
                "value": {
                    **info_base_data,
                    "area": areas_data,
                },
            }
            
            info_blocks.append(stream_item)
    
    if not title:
        raise CAPAlertImportError("Could not extract title from CAP Alert data")
    
    base_data["title"] = title
    
    new_cap_alert_page = CapAlertPage(**base_data, live=False)
    new_cap_alert_page.info = StreamValue(new_cap_alert_page.info.stream_block, info_blocks, is_lazy=True)
    
    cap_list_page = CapAlertListPage.objects.live().first()
    
    if cap_list_page:
        cap_list_page.add_child(instance=new_cap_alert_page)
        new_cap_alert_page.save_revision()
        
        return new_cap_alert_page
    
    return None


def get_first_page_of_pdf_as_image(file_path, title, file_name):
    with tempfile.TemporaryDirectory() as path:
        images = convert_from_path(file_path, output_folder=path, single_file=True)
        if images:
            buffer = io.BytesIO()
            images[0].save(buffer, format='JPEG')
            buff_val = buffer.getvalue()
            
            content_file = ContentFile(buff_val, f"{file_name}")
            image = get_image_model().objects.create(title=title, file=content_file)
            return image
    
    return None


def get_full_url_by_site(site, path):
    base_url = site.root_url
    
    # We only want the scheme and netloc
    base_url_parsed = urlsplit(force_str(base_url))
    
    base_url = base_url_parsed.scheme + "://" + base_url_parsed.netloc
    
    return base_url + path
