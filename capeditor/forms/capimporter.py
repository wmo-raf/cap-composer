import requests
from django import forms
from django.utils.translation import gettext_lazy as _

from capeditor.caputils import cap_xml_to_alert_data
from capeditor.errors import CAPImportError


class CAPImportForm(forms.Form):
    from_file = forms.BooleanField(required=False, label=_('Load from file'))
    url = forms.URLField(required=False, label=_('CAP Alert XML URL'))
    file = forms.FileField(required=False, label=_('CAP File'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['file'].widget.attrs.update({'accept': '.xml'})

    def clean(self):
        cleaned_data = super().clean()
        from_file = cleaned_data.get('from_file')
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')

        if from_file and not file:
            self.add_error('file', _('This field is required.'))
        elif not from_file and not url:
            self.add_error('url', _('This field is required.'))

        try:
            if from_file:
                file = cleaned_data.get('file')
                content = file.read().decode('utf-8')
            else:
                url = cleaned_data.get('url')
                res = requests.get(url)
                res.raise_for_status()

                content = res.text

            alert_data = cap_xml_to_alert_data(content)
            cleaned_data['alert_data'] = alert_data

        except CAPImportError as e:
            self.add_error(None, e.message)
            return cleaned_data

        except Exception as e:
            print(e)
            self.add_error(None, _("An error occurred while trying to load the CAP XML. "
                                   "Please check the data and try again."))
            return cleaned_data

        return cleaned_data
