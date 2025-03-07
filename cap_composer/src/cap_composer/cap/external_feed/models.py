from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import PeriodicTask
from wagtail.admin.panels import FieldPanel


class ExternalAlertFeed(models.Model):
    FEED_TYPES = (
        ('rss', 'RSS'),
        ('atom', 'Atom'),
    )
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Feed name"),
                            help_text=_("Provide a name to identify the feed"), )
    feed_type = models.CharField(max_length=4, choices=FEED_TYPES, blank=True, null=True, verbose_name=_("Feed Type"),
                                 help_text=_("Select the type of feed"))
    url = models.URLField(unique=True, verbose_name=_("Feed URL"), help_text=_("Enter the URL of the feed"), )
    active = models.BooleanField(default=True, verbose_name=_("Active"),
                                 help_text=_("Automatically fetch data from this feed. Uncheck to disable."))
    check_interval = models.PositiveIntegerField(default=5, verbose_name=_("Feed check interval in minutes"),
                                                 validators=[
                                                     MinValueValidator(1),
                                                     MaxValueValidator(10)
                                                 ],
                                                 help_text=_("How often to check for new alerts in minutes. "
                                                             "Min: 1, Max: 10"))
    validate_xml_signature = models.BooleanField(default=False, verbose_name=_("Validate CAP XML Signature"),
                                                 help_text=_("Check to only import alerts with a valid XML signature."))
    last_checked = models.DateTimeField(blank=True, null=True)
    periodic_task = models.ForeignKey(PeriodicTask, null=True, on_delete=models.SET_NULL)
    submit_for_moderation = models.BooleanField(default=True, verbose_name=_("Submit imported alerts"
                                                                             " for moderation"),
                                                help_text=_("Check to automatically submit imported alerts "
                                                            "for moderation. Otherwise, alerts will be saved as drafts."))
    
    panels = [
        FieldPanel('name'),
        FieldPanel('url'),
        FieldPanel('active'),
        FieldPanel('check_interval'),
        FieldPanel('validate_xml_signature'),
        FieldPanel('submit_for_moderation'),
    ]
    
    class Meta:
        verbose_name = _("External Alert Feed")
        verbose_name_plural = _("External Alert Feeds")
    
    def __str__(self):
        return f"{self.name} - {self.url}"


class ExternalAlertFeedEntry(models.Model):
    feed = models.ForeignKey(ExternalAlertFeed, on_delete=models.CASCADE, related_name='alerts')
    url = models.URLField(unique=True, verbose_name=_("Alert URL"), help_text=_("The URL of the alert XML"))
    remote_alert_id = models.CharField(max_length=255, verbose_name=_("Remote Alert ID"),
                                       help_text=_("The unique identifier of the alert in the remote feed"))
    imported_alert = models.OneToOneField("cap.CapAlertPage", null=True, on_delete=models.CASCADE,
                                          related_name='external_feed_entry',
                                          help_text=_("The imported alert from this entry"))
    
    class Meta:
        verbose_name = _("External Alert Feed Entry")
        verbose_name_plural = _("External Alert Feed Entries")
    
    def __str__(self):
        return self.remote_alert_id


@receiver(post_save, sender=ExternalAlertFeed)
def update_external_feed_periodic_task(sender, instance, **kwargs):
    from cap.tasks import create_or_update_alert_feed_periodic_tasks
    create_or_update_alert_feed_periodic_tasks(instance)


@receiver(post_delete, sender=ExternalAlertFeed)
def update_external_feed_periodic_task(sender, instance, **kwargs):
    from cap.tasks import create_or_update_alert_feed_periodic_tasks
    create_or_update_alert_feed_periodic_tasks(instance, delete=True)
