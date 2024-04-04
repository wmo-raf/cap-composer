from adminboundarymanager.wagtail_hooks import AdminBoundaryManagerAdminGroup
from django.shortcuts import redirect
from django.urls import reverse
from wagtail import hooks
from wagtail.blocks import StreamValue
from wagtail_modeladmin.options import (
    modeladmin_register
)

from capeditor.cap_settings import CapSetting
from .models import CapAlertPage, HomePage

modeladmin_register(AdminBoundaryManagerAdminGroup)


@hooks.register("before_import_cap_alert")
def import_cap_alert(request, alert_data):
    cap_settings = CapSetting.for_request(request)
    hazard_event_types = cap_settings.hazard_event_types.all()

    base_data = {}

    title = None

    if "sender" in alert_data:
        base_data["sender"] = alert_data["sender"]
    if "sent" in alert_data:
        base_data["sent"] = alert_data["sent"]

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
                info_base_data["language"] = info["language"]
            if "category" in info:
                info_base_data["category"] = info["category"]
            if "event" in info:
                event = info["event"]

                if hazard_event_types.filter(event__iexact=event).exists():
                    hazard_event_type = hazard_event_types.get(event=event)
                    info_base_data["event"] = hazard_event_type.event
                else:
                    hazard_event_types.create(setting=cap_settings, event=event)
                    info_base_data["event"] = event

            if "responseType" in info:
                pass
            if "urgency" in info:
                info_base_data["urgency"] = info["urgency"]
            if "severity" in info:
                info_base_data["severity"] = info["severity"]
            if "certainty" in info:
                info_base_data["certainty"] = info["certainty"]
            if "audience" in info:
                info_base_data["audience"] = info["audience"]
            if "eventCode" in info:
                pass
            if "effective" in info:
                info_base_data["effective"] = info["effective"]
            if "onset" in info:
                info_base_data["onset"] = info["onset"]
            if "expires" in info:
                info_base_data["expires"] = info["expires"]
            if "senderName" in info:
                info_base_data["senderName"] = info["senderName"]
            if "headline" in info:
                info_base_data["headline"] = info["headline"]
                if not title:
                    title = info["headline"]

            if "description" in info:
                info_base_data["description"] = info["description"]
            if "instruction" in info:
                info_base_data["instruction"] = info["instruction"]
            if "contact" in info:
                info_base_data["contact"] = info["contact"]
            if "parameter" in info:
                pass
            if "resource" in info:
                pass

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
                        polygon_data["polygon"] = geometry

                        area_data["value"] = polygon_data

                    if "circle" in area:
                        area_data["type"] = "circle_block"
                        circle_data = {
                            "areaDesc": areaDesc,
                        }
                        circle = area.get("circle")
                        circle_data["circle"] = circle
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

    if title:
        base_data["title"] = title
        new_cap_alert_page = CapAlertPage(**base_data, live=False)
        new_cap_alert_page.info = StreamValue(new_cap_alert_page.info.stream_block, info_blocks, is_lazy=True)

        cap_list_page = HomePage.objects.live().first()

        if cap_list_page:
            cap_list_page.add_child(instance=new_cap_alert_page)
            cap_list_page.save_revision()

            return redirect(reverse("wagtailadmin_pages:edit", args=[new_cap_alert_page.id]))

    return None
