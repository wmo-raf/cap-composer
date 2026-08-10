import django.db.models.deletion
from django.db import migrations, models


def assign_default_site(apps, schema_editor):
    Site = apps.get_model('wagtailcore', 'Site')
    default_site = Site.objects.filter(is_default_site=True).first()
    if not default_site:
        return

    CAPAlertMQTTBroker = apps.get_model('cap', 'CAPAlertMQTTBroker')
    CAPAlertWebhook = apps.get_model('cap', 'CAPAlertWebhook')
    ExternalAlertFeed = apps.get_model('cap', 'ExternalAlertFeed')

    CAPAlertMQTTBroker.objects.filter(site__isnull=True).update(site=default_site)
    CAPAlertWebhook.objects.filter(site__isnull=True).update(site=default_site)
    ExternalAlertFeed.objects.filter(site__isnull=True).update(site=default_site)


class Migration(migrations.Migration):

    dependencies = [
        ('cap', '0033_capalertwebhook_header_value_and_more'),
        ('wagtailcore', '0094_alter_page_locale'),
    ]

    operations = [
        migrations.AddField(
            model_name='capalertmqttbroker',
            name='site',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='mqtt_brokers',
                to='wagtailcore.site',
                verbose_name='Site',
            ),
        ),
        migrations.AddField(
            model_name='capalertwebhook',
            name='site',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='webhooks',
                to='wagtailcore.site',
                verbose_name='Site',
            ),
        ),
        migrations.AddField(
            model_name='externalalertfeed',
            name='site',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='external_feeds',
                to='wagtailcore.site',
                verbose_name='Site',
            ),
        ),
        migrations.RunPython(assign_default_site, migrations.RunPython.noop),
    ]
