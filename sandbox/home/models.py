import json
from datetime import datetime

from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _, gettext_lazy
from wagtail.admin.panels import MultiFieldPanel, FieldPanel
from wagtail.admin.widgets.slug import SlugInput
from wagtail.images import get_image_model_string
from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.signals import page_published

from capeditor.models import AbstractCapAlertPage
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
            'active_alerts': CapAlertPage.objects.filter(info__in=active_alert_infos),
            'geojson': json.dumps(geojson)
        }


class CapAlertPage(AbstractCapAlertPage):
    template = "home/cap_alert_detail.html"

    parent_page_type = ["home.HomePage"]
    subpage_types = []
    exclude_fields_in_copy = ["identifier", ]

    """An implementation of MetadataMixin for Wagtail pages."""
    search_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        verbose_name=gettext_lazy('Search image')
    )

    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels
    ]

    promote_panels = [
        MultiFieldPanel(
            [
                FieldPanel("slug", widget=SlugInput),
                FieldPanel("seo_title"),
                FieldPanel('show_in_menus'),
                FieldPanel("search_description"),
                FieldPanel('search_image'),
            ],
            gettext_lazy("For search engines"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_in_menus"),
            ],
            gettext_lazy("For site menus"),
        ),
    ]

    class Meta:
        verbose_name = _("CAP Alert Page")
        verbose_name_plural = _("CAP Alert Pages")

    @cached_property
    def xml_link(self):
        return reverse("cap_alert_detail", args=(self.identifier,))


def on_publish_cap_alert(sender, **kwargs):
    instance = kwargs['instance']

    try:
        # publish to mqtt
        topic = "cap/alerts/all"
        publish_cap_mqtt_message(instance, topic)
    except Exception as e:
        pass

    try:
        # create summary image
        image_content_file = instance.generate_alert_card_image()
        if image_content_file:

            # delete old image
            if instance.search_image:
                instance.search_image.delete()

            # create new image
            instance.search_image = Image(title=instance.title, file=image_content_file)
            instance.search_image.save()

            # save the instance
            instance.save()
    except Exception as e:
        pass


page_published.connect(on_publish_cap_alert, sender=CapAlertPage)
