import requests
from django import forms
from django.utils.translation import gettext_lazy as _

from capeditor.caputils import cap_xml_to_alert_data
from capeditor.errors import CAPImportError


class CAPLoadForm(forms.Form):
    LOAD_FROM_CHOICES = (
        ('text', _('Copy Paste XML')),
        ('url', _('URL')),
        ('file', _('File')),
    )

    load_from = forms.ChoiceField(choices=LOAD_FROM_CHOICES, initial="text", widget=forms.RadioSelect,
                                  label=_('Load from'), )
    text = forms.CharField(required=False, widget=forms.Textarea, label=_('Paste your CAP XML here'))
    url = forms.URLField(required=False, label=_('CAP Alert XML URL'))
    file = forms.FileField(required=False, label=_('CAP File'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': '.xml'})

    def clean(self):
        cleaned_data = super().clean()
        load_from = cleaned_data.get('load_from')
        text = cleaned_data.get('text')
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')

        # field validation
        if load_from == 'text' and not text:
            self.add_error('text', _('This field is required.'))
        if load_from == 'url' and not url:
            self.add_error('url', _('This field is required.'))
        if load_from == 'file' and not file:
            self.add_error('file', _('This field is required.'))

        try:
            if load_from == 'text':
                content = cleaned_data.get('text')
                alert_source = {
                    "type": "Copied XML",
                }
            elif load_from == 'file':
                file = cleaned_data.get('file')
                content = file.read().decode('utf-8')
                alert_source = {
                    "name": file.name,
                    "type": "File",
                }
            else:
                url = cleaned_data.get('url')
                res = requests.get(url)
                res.raise_for_status()
                content = res.text
                alert_source = {
                    "name": url,
                    "type": "URL",
                }

            alert_data = cap_xml_to_alert_data(content)

            alert_data['alert_source'] = alert_source

            cleaned_data['alert_data'] = alert_data

        except CAPImportError as e:
            self.add_error(None, e.message)
            return cleaned_data

        except Exception as e:
            self.add_error(None, _("An error occurred while trying to load the CAP XML. "
                                   "Please check the data and try again."))
            return cleaned_data

        return cleaned_data


class CAPImportForm(forms.Form):
    alert_data = forms.JSONField(widget=forms.HiddenInput)
