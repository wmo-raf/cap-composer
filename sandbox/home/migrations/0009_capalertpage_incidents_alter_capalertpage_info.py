# Generated by Django 4.1.10 on 2023-07-07 14:19

import capeditor.blocks
from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_capalertpage_references_alter_capalertpage_addresses'),
    ]

    operations = [
        migrations.AddField(
            model_name='capalertpage',
            name='incidents',
            field=wagtail.fields.StreamField([('incident', wagtail.blocks.StructBlock([('incident', wagtail.blocks.TextBlock(help_text='Referent incident to this alert message', label='Incident'))], label='Referent Incident'))], blank=True, null=True, use_json_field=True, verbose_name='Incidents'),
        ),
        migrations.AlterField(
            model_name='capalertpage',
            name='info',
            field=wagtail.fields.StreamField([('alert_info', wagtail.blocks.StructBlock([('language', wagtail.blocks.ChoiceBlock(choices=[('en', 'English')], help_text='The code denoting the language of the alert message', label='Language', required=False)), ('category', wagtail.blocks.ChoiceBlock(choices=[('Geo', 'Geophysical'), ('Met', 'Meteorological'), ('Safety', 'General emergency and public safety'), ('Security', 'Law enforcement, military, homeland and local/private security'), ('Rescue', 'Rescue and recovery'), ('Fire', 'Fire suppression and rescue'), ('Health', 'Medical and public health'), ('Env', 'Pollution and other environmental'), ('Transport', 'Public and private transportation'), ('Infra', 'Utility, telecommunication, other non-transport infrastructure'), ('Cbrne', 'Chemical, Biological, Radiological, Nuclear or High-Yield Explosive threat or attack'), ('Other', 'Other events')], help_text='The code denoting the category of the subject event of the alert message', label='Category')), ('event', wagtail.blocks.CharBlock(help_text='The text denoting the type of the subject event of the alert message', label='Event', max_length=255)), ('urgency', wagtail.blocks.ChoiceBlock(choices=[('Immediate', 'Immediate - Responsive action SHOULD be taken immediately'), ('Expected', 'Expected - Responsive action SHOULD be taken soon (within next hour)'), ('Future', 'Future - Responsive action SHOULD be taken in the near future'), ('Past', 'Past - Responsive action is no longer required'), ('Unknown', 'Unknown - Urgency not known')], help_text='The code denoting the urgency of the subject event of the alert message', label='Urgency')), ('severity', wagtail.blocks.ChoiceBlock(choices=[('Extreme', 'Extreme - Extraordinary threat to life or property'), ('Severe', 'Severe - Significant threat to life or property'), ('Moderate', 'Moderate - Possible threat to life or property'), ('Minor', 'Minor - Minimal to no known threat to life or property'), ('Unknown', 'Unknown - Severity unknown')], help_text='The code denoting the severity of the subject event of the alert message', label='Severity')), ('certainty', wagtail.blocks.ChoiceBlock(choices=[('Observed', 'Observed - Determined to have occurred or to be ongoing'), ('Likely', 'Likely - Likely (percentage > ~50%)'), ('Possible', 'Possible - Possible but not likely (percentage <= ~50%)'), ('Unlikely', 'Unlikely - Not expected to occur (percentage ~ 0)'), ('Unknown', 'Unknown - Certainty unknown')], help_text='The code denoting the certainty of the subject event of the alert message', label='Certainty')), ('headline', wagtail.blocks.CharBlock(help_text='The text headline of the alert message. Make it direct and actionable as possible while remaining short', label='Headline', max_length=160, required=False)), ('description', wagtail.blocks.TextBlock(help_text='The text describing the subject event of the alert message. An extended description of the hazard or event that occasioned this message', label='Description', required=True)), ('instruction', wagtail.blocks.TextBlock(help_text='The text describing the recommended action to be taken by recipients of the alert message', label='Instruction', required=False)), ('effective', wagtail.blocks.DateTimeBlock(help_text='The effective time of the information of the alert message. If not set, the sent date will be used', label='Effective', required=False)), ('onset', wagtail.blocks.DateTimeBlock(help_text='The expected time of the beginning of the subject event of the alert message', label='Onset', required=False)), ('expires', wagtail.blocks.DateTimeBlock(help_text='The expiry time of the information of the alert message. If not set, each recipient is free to set its own policy as to when the message is no longer in effect.', label='Expires', required=True)), ('senderName', wagtail.blocks.CharBlock(help_text='The human-readable name of the agency or authority issuing this alert.', label='Sender name', max_length=255, required=False)), ('contact', wagtail.blocks.CharBlock(help_text='The text describing the contact for follow-up and confirmation of the alert message', label='Contact', max_length=255, required=False)), ('audience', wagtail.blocks.CharBlock(help_text='The text describing the intended audience of the alert message', label='Audience', max_length=255, required=False)), ('area', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('areaDesc', wagtail.blocks.TextBlock(help_text='The text describing the affected area of the alert message', label='Affected areas / Regions')), ('polygon', capeditor.blocks.PolygonFieldBlock(help_text='The paired values of points defining a polygon that delineates the affected area of the alert message', label='Polygon')), ('altitude', wagtail.blocks.CharBlock(help_text='The specific or minimum altitude of the affected area of the alert message', label='Altitude', max_length=100, required=False)), ('ceiling', wagtail.blocks.CharBlock(help_text='The maximum altitude of the affected area of the alert message.MUST NOT be used except in combination with the altitude element. ', label='Ceiling', max_length=100, required=False))]), label='Alert Areas', min_num=1)), ('parameter', wagtail.blocks.ListBlock(wagtail.blocks.StructBlock([('valueName', wagtail.blocks.TextBlock(label='Name')), ('value', wagtail.blocks.TextBlock(label='Value'))], label='Parameter'), default=[], label='Parameters'))], label='Alert Information'))], blank=True, null=True, use_json_field=True, verbose_name='Alert Information'),
        ),
    ]
