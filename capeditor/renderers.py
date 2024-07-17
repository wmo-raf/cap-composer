import datetime
import xml.etree.ElementTree as ET
from io import StringIO

from rest_framework_xml.renderers import XMLRenderer


class CapXMLRenderer(XMLRenderer):
    format = 'xml'
    root_tag_name = 'alert'

    def _recursive_serialize_dict(self, value, parent):
        for key, value in value.items():
            if isinstance(value, list):
                # handle MULTIPOLYGONS
                if key == 'polygons':
                    for polygon_coords in value:
                        element = ET.SubElement(parent, "cap:polygon")
                        self._recursive_serialize(polygon_coords, element)
                else:
                    for item in value:
                        element = ET.SubElement(parent, f"cap:{key}")
                        self._recursive_serialize(item, element)

            else:
                element = ET.SubElement(parent, f"cap:{key}")
                self._recursive_serialize(value, element)

    def _recursive_serialize(self, value, element):
        if isinstance(value, dict):
            self._recursive_serialize_dict(value, element)
        elif isinstance(value, datetime.datetime):
            element.text = value.isoformat()
        elif isinstance(value, (int, float)):
            element.text = str(value)
        elif isinstance(value, str):
            element.text = value
        elif value is None:
            element.set('nil', 'true')
        else:
            element.text = str(value)

    def render(self, data, accepted_media_type=None, renderer_context=None):
        """
        Render `data` into XML.
        """
        tree = ET.ElementTree()
        stream = StringIO()

        if data is None:
            return ''

        if not isinstance(data, dict):
            raise ValueError('Data should be a dictionary')

        root = ET.Element('cap:alert', attrib={'xmlns:cap': 'urn:oasis:names:tc:emergency:cap:1.2'})

        self._recursive_serialize_dict(data, root)
        tree._setroot(root)
        tree.write(stream, encoding="unicode", xml_declaration=True)

        return stream.getvalue()
