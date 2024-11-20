from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel


class CAPAlertWebhook(ClusterableModel):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    url = models.URLField(max_length=255, unique=True, verbose_name=_("Webhook URL"))
    active = models.BooleanField(default=True, verbose_name=_("Active"))
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    retry_on_failure = models.BooleanField(default=True, verbose_name=_("Retry on failure"))

    panels = [
        FieldPanel("name"),
        FieldPanel("url"),
        FieldPanel("active"),
    ]

    class Meta:
        verbose_name = _("CAP Alert Webhook")
        verbose_name_plural = _("CAP Alert Webhooks")

    def __str__(self):
        return f"{self.name} - {self.url}"


WEBHOOK_STATES = [
    ("PENDING", _("Pending")),
    ("FAILURE", _("Failure")),
    ("SUCCESS", _("Success")),
]


class CAPAlertWebhookEvent(models.Model):
    webhook = models.ForeignKey(CAPAlertWebhook, on_delete=models.CASCADE, related_name="events")
    alert = models.ForeignKey("cap.CapAlertPage", on_delete=models.CASCADE, related_name="webhook_events")
    status = models.CharField(max_length=40, choices=WEBHOOK_STATES, default="PENDING", verbose_name=_("Status"),
                              editable=False, )
    retries = models.IntegerField(default=0, verbose_name=_("Retries"))
    error = models.TextField(blank=True, null=True, verbose_name=_("Last Error Message"), )
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("CAP Alert Webhook Event")
        verbose_name_plural = _("CAP Alert Webhook Events")

    def __str__(self):
        return f"{self.webhook.name} - {self.alert.title}"
