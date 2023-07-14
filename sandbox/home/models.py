from django.urls import reverse
from django.utils.functional import cached_property
from wagtail.models import Page

from capeditor.models import AbstractCapAlertPage


class HomePage(Page):
    subpage_types = ["home.CapAlertPage"]
    pass


class CapAlertPage(AbstractCapAlertPage):
    template = "capeditor/cap_alert_page.html"

    parent_page_type = ["home.HomePage"]
    subpage_types = []

    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels
    ]

    

    @cached_property
    def xml_link(self):
        return reverse("cap_alert_detail", args=(self.identifier,))
