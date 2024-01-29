import datetime
from io import StringIO
from xml.etree.ElementTree import Element, ElementTree

import six
from rest_framework_xml.renderers import XMLRenderer


class CapXMLRenderer(XMLRenderer):
    format = 'xml'
    root_tag_name = 'alert'

    def _recursive_serialize_dict(self, value, xml):
        for key, value in value.items():
            if isinstance(value, list):
                # handle MULTIPOLYGONS
                if key == 'polygons':
                    for polygon_coords in value:
                        element = Element("polygon")
                        self._recursive_serialize(polygon_coords, element)
                        xml.append(element)
                else:
                    for item in value:
                        element = Element(key)
                        self._recursive_serialize(item, element)
                        xml.append(element)
            else:
                element = Element(key)
                self._recursive_serialize(value, element)
                xml.append(element)

    def _recursive_serialize(self, value, xml):
        if isinstance(value, dict):
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

        tree = ElementTree()
        stream = StringIO()

        if data is None:
            return ''
        elif isinstance(data, list):
            root = Element('feed')

            for item in data:
                element = Element('alert')
                element.set('xmlns', 'urn:oasis:names:tc:emergency:cap:1.2')
                self._recursive_serialize(item, element)

                root.append(element)

            tree._setroot(root)
            tree.write(stream, encoding="unicode", xml_declaration=True)

            return stream.getvalue()

        elif isinstance(data, dict):

            root = Element('alert')
            root.set('xmlns', 'urn:oasis:names:tc:emergency:cap:1.2')

            self._recursive_serialize_dict(data, root)

            tree._setroot(root)
            tree.write(stream, encoding="unicode", xml_declaration=True)

            return stream.getvalue()
        else:
            return data
