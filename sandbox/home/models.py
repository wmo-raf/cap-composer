from wagtail.models import Page

from capeditor.models import AbstractCapAlertPage


class HomePage(Page):
    subpage_types = ["home.CapAlertPage"]
    pass


class CapAlertPage(AbstractCapAlertPage):
    template = "cap/cap_alert_page.html"
    parent_page_type = ["home.HomePage"]

    content_panels = Page.content_panels + [
        *AbstractCapAlertPage.content_panels
    ]
