# Generated by Django 4.2.7 on 2024-11-07 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('capeditor', '0009_capsetting_un_country_boundary_geojson'),
    ]

    operations = [
        migrations.AlterField(
            model_name='capsetting',
            name='un_country_boundary_geojson',
            field=models.JSONField(blank=True, help_text='GeoJSON file of the UN Country Boundary. Setting this will enable the UN Country Boundary check in the alertdrawing tools', null=True, verbose_name='UN Country Boundary'),
        ),
    ]