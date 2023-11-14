from django.urls import reverse
from django.utils.functional import cached_property
from wagtail.models import Page
from django.utils.translation import gettext_lazy as _

from capeditor.models import AbstractCapAlertPage
import json
from datetime import datetime, timedelta
from wagtail.signals import page_published

from capeditor.pubsub.publish import publish_cap_mqtt_message


class HomePage(Page):
    subpage_types = ["home.CapAlertPage"]
    pass

    @cached_property
    def get_alerts(self):
        alerts = CapAlertPage.objects.all().order_by('-sent')[:2]        

        active_alert_infos = []

        geojson = {"type": "FeatureCollection", "features": []}

        for alert in alerts:
            for info in alert.info:
                if info.value.get('expires').date() >= datetime.today().date():

                    active_alert_infos.append(alert.info)
                    # print(info.value.id)

                    if info.value.features:
                        for feature in info.value.features:
                            geojson["features"].append(feature)

        # print(CapAlertPage.objects.filter(info__in = active_alert_infos ))
        return {
            'active_alerts': CapAlertPage.objects.filter(info__in = active_alert_infos ),
            'geojson':json.dumps(geojson)
        }


class CapAlertPage(AbstractCapAlertPage):
    template = "capeditor/cap_alert_page.html"

    parent_page_type = ["home.HomePage"]
    subpage_types = []
    exclude_fields_in_copy = ["identifier", ]

    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels
    ]

    class Meta:
        verbose_name = _("CAP Alert Page")
        verbose_name_plural = _("CAP Alert Pages")
    
    
    @cached_property
    def xml_link(self):
        return reverse("cap_alert_detail", args=(self.identifier,))


def on_publish_cap_alert(sender, **kwargs):
    instance = kwargs['instance']

    topic = "cap/alerts/all"

    publish_cap_mqtt_message(instance, topic)


page_published.connect(on_publish_cap_alert, sender=CapAlertPage)
