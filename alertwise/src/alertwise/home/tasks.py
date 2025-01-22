import logging

from celery.schedules import crontab
from celery_singleton import Singleton
from django.core.management import call_command

from alertwise.utils import get_celery_app

logger = logging.getLogger(__name__)

app = get_celery_app()


@app.task(
    base=Singleton,
    bind=True
)
def run_backup(self):
    # Run the `dbbackup` command
    call_command('dbbackup', '--clean', '--noinput')
    
    # Run the `mediabackup` command
    call_command('mediabackup', '--clean', '--noinput')


@app.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    # run_backup every day at midnight
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        run_backup.s(),
        name="run-backup-every-day-midnight",
    )
