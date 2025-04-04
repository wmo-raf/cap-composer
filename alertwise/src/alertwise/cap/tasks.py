import json
import logging

from celery.signals import worker_ready
from celery_singleton import Singleton, clear_locks
from django.utils.text import slugify
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from alertwise.utils import get_celery_app
from .external_feed.utils import fetch_and_process_feed
from .models import CapAlertPage, ExternalAlertFeed
from .mqtt.publish import publish_cap_to_all_mqtt_brokers
from .utils import create_cap_alert_multi_media
from .webhook.utils import fire_alert_webhooks

logger = logging.getLogger(__name__)

app = get_celery_app()


@worker_ready.connect
def unlock_all(**kwargs):
    clear_locks(app)


@app.task(base=Singleton, bind=True)
def check_alert_feed(self, feed_id):
    feed = ExternalAlertFeed.objects.get(id=feed_id)
    
    logger.info(f"Checking external feed {feed.name}...")
    
    fetch_and_process_feed(feed_id)


@app.task(base=Singleton, bind=True)
def handle_publish_alert_to_mqtt(self, alert_id):
    alert = CapAlertPage.objects.get(id=alert_id)
    logger.info(f"Publishing alert '{alert}' to MQTT brokers...")
    publish_cap_to_all_mqtt_brokers(alert.id)


@app.task(base=Singleton, bind=True)
def handle_publish_alert_to_webhook(self, alert_id):
    alert = CapAlertPage.objects.get(id=alert_id)
    logger.info(f"Publishing alert '{alert}' to HTTP webhooks...")
    fire_alert_webhooks(alert.id)


@app.task(base=Singleton, bind=True)
def handle_generate_multimedia(self, alert_id):
    alert = CapAlertPage.objects.get(id=alert_id)
    logger.info(f"Generating CAP multimedia for alert '{alert}'...")
    
    # delete previous pdf preview if exists
    if alert.alert_pdf_preview:
        alert.alert_pdf_preview.delete()
    
    if alert.search_image:
        alert.search_image.delete()
    
    if alert.alert_area_map_image:
        alert.alert_area_map_image.delete()
    
    create_cap_alert_multi_media(alert.pk, clear_cache_on_success=True)


def create_or_update_alert_feed_periodic_tasks(external_feed, delete=False):
    periodic_task = None
    if external_feed.periodic_task:
        periodic_task = external_feed.periodic_task
    
    if periodic_task and delete:
        periodic_task.delete()
        return
    
    interval = external_feed.check_interval
    enabled = external_feed.active
    feed_name = external_feed.name
    sig = check_alert_feed.s(external_feed.id)
    name = slugify(f"Check External Alert Feed {feed_name}")
    
    # try to get a task that might match this name
    if not periodic_task:
        periodic_task = PeriodicTask.objects.filter(name=name).first()
    
    schedule, created = IntervalSchedule.objects.get_or_create(
        every=interval,
        period=IntervalSchedule.MINUTES,
    )
    
    if periodic_task:
        periodic_task.name = name
        periodic_task.interval = schedule
        periodic_task.task = sig.name
        periodic_task.args = json.dumps([external_feed.id])
        periodic_task.enabled = enabled
        periodic_task.save()
    else:
        periodic_task = PeriodicTask.objects.create(
            name=name,
            interval=schedule,
            task=sig.name,
            args=json.dumps([external_feed.id]),
            enabled=enabled
        )
        external_feed.periodic_task = periodic_task
        external_feed.save()


@app.on_after_finalize.connect
def setup_feed_processing_tasks(sender, **kwargs):
    external_feeds = ExternalAlertFeed.objects.all()
    
    for feed in external_feeds:
        create_or_update_alert_feed_periodic_tasks(feed)
