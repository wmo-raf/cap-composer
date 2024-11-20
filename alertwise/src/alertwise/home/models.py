from dataclasses import Field

from adminboundarymanager.models import AdminBoundarySettings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from wagtail.admin.panels import FieldPanel
from wagtail.models import Page, Site

from alertwise.cap.models import CapAlertPage, CapAlertListPage


class HomePage(Page):
    max_count = 1
    subpage_types = [
        "cap.CapAlertListPage"
    ]
    
    subtitle = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Subtitle"))
    
    content_panels = Page.content_panels + [
        FieldPanel("subtitle")
    ]
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request)
        sites = Site.objects.all()
        
        linked_sites = []
        cap_list_pages = CapAlertListPage.objects.live()
        
        for site in sites:
            for cap_list_page in cap_list_pages:
                
                if cap_list_page.get_site() == site:
                    adm_boundary_setting = AdminBoundarySettings.for_site(site)
                    country = adm_boundary_setting.countries.first()
                    
                    site_info = {
                        "site": site,
                        "cap_list_page": cap_list_page
                    }
                    
                    if country:
                        site_info["country"] = country
                    
                    linked_sites.append(site_info)
        
        context["linked_sites"] = linked_sites
        
        return context


@cached_property
def cap_alerts(self):
    alerts = CapAlertPage.objects.all().live().filter(status="Actual").order_by('-sent')
    alert_infos = []
    
    for alert in alerts:
        for alert_info in alert.infos:
            alert_infos.append(alert_info)
    
    alert_infos = sorted(alert_infos, key=lambda x: x.get("sent", {}), reverse=True)
    
    return alert_infos


@cached_property
def alerts_by_expiry(self):
    all_alerts = self.cap_alerts
    active_alerts = []
    past_alerts = []
    
    for alert in all_alerts:
        if alert.get("expired"):
            past_alerts.append(alert)
        else:
            active_alerts.append(alert)
    
    return {
        "active_alerts": active_alerts,
        "past_alerts": past_alerts
    }
