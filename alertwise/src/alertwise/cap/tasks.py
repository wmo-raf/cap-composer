import json
import logging

from celery.signals import worker_ready
from celery_singleton import Singleton, clear_locks
from django.utils.text import slugify
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from alertwise.utils import get_celery_app
from .external_feed.utils import fetch_and_process_feed
from .models import ExternalAlertFeed
from .utils import get_object_or_none

logger = logging.getLogger(__name__)

app = get_celery_app()


@worker_ready.connect
def unlock_all(**kwargs):
    clear_locks(app)


@app.task(
    base=Singleton,
    bind=True
)
def check_alert_feed(self, feed_id):
    feed = get_object_or_none(ExternalAlertFeed, id=feed_id)
    
    if not feed:
        logger.error(f"ExternalAlertFeed with id {feed_id} does not exist. Skipping...")
        return
    
    logger.info(f"Checking feed {feed.name}...")
    
    fetch_and_process_feed(feed_id)


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
