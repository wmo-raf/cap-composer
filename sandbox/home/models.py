from django.urls import reverse
from django.utils.functional import cached_property
from wagtail.models import Page
from wagtail.signals import page_published

from capeditor.models import AbstractCapAlertPage
from capeditor.pubsub.publish import publish_cap_mqtt_message


class HomePage(Page):
    subpage_types = ["home.CapAlertPage"]
    pass


class CapAlertPage(AbstractCapAlertPage):
    template = "capeditor/cap_alert_page.html"

    parent_page_type = ["home.HomePage"]
    subpage_types = []
    exclude_fields_in_copy = ["identifier", ]

    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels
    ]

    @cached_property
    def xml_link(self):
        return reverse("cap_alert_detail", args=(self.identifier,))


def on_publish_cap_alert(sender, **kwargs):
    instance = kwargs['instance']

    topic = "cap/alerts/all"

    publish_cap_mqtt_message(instance, topic)


page_published.connect(on_publish_cap_alert, sender=CapAlertPage)
