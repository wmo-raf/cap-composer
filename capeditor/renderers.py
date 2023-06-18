# from io import StringIO
# from rest_framework_xml.renderers import XMLRenderer
import six
import datetime

from rest_framework_xml.renderers import XMLRenderer
from xml.etree.ElementTree import Element, tostring


class CustomXMLRenderer(XMLRenderer):
    format = 'xml'
    root_tag_name = 'alert'

    def _recursive_serialize_dict(self, value, xml):
        for key, value in value.items():
            if isinstance(value, list):
                for item in value:
                    element = Element(key)
                    self._recursive_serialize(item, element)
                    xml.append(element)
            else:
                element = Element(key)
                self._recursive_serialize(value, element)
                xml.append(element)

    def _recursive_serialize(self, value, xml):

        if isinstance(value, (list, tuple)):
            self._recursive_serialize_list(value, xml)
        elif isinstance(value, dict):
            self._recursive_serialize_dict(value, xml)
        elif isinstance(value, datetime.datetime):
            xml.text = value.isoformat()
        elif isinstance(value, (six.integer_types, float)):
            xml.text = six.text_type(value)
        elif isinstance(value, six.text_type):
            xml.text = value
        elif value is None:
            xml.set('nil', 'true')
        else:
            xml.text = six.text_type(value)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into XML.
        """
        if data is None:
            return ''
        elif isinstance(data, list):
            root = Element('feed')
            root.set('xmlns', 'urn:oasis:names:tc:emergency:cap:1.2')

            for item in data:
                element = Element('alert')
                self._recursive_serialize(item, element)

                root.append(element)

            return tostring(root, encoding='unicode')
        elif isinstance(data, dict):
            root = Element('alert')
            root.set('xmlns', 'urn:oasis:names:tc:emergency:cap:1.2')

            self._recursive_serialize_dict(data, root)
            return tostring(root, encoding='unicode')
        else:
            return data
