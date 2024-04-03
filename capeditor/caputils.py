from xmltodict import parse as parse_xml_to_dict

from capeditor.errors import CAPImportError

CAP_ALERT_ELEMENTS = [
    {
        "name": "identifier",
        "required": True,
    },
    {
        "name": "sender",
        "required": True,
    },
    {
        "name": "sent",
        "required": True,
    },
    {
        "name": "status",
        "required": True,
    },
    {
        "name": "msgType",
        "required": True,
    },
    {
        "name": "scope",
        "required": True,
    },
    {
        "name": "restriction",
        "required": False,
    },
    {
        "name": "addresses",
        "required": False,
    },
    {
        "name": "code",
        "required": False,
        "many": True,
    },
    {
        "name": "note",
        "required": False,
    },
    {
        "name": "references",
        "required": False,
    },
    {
        "name": "incidents",
        "required": False,
    },
    {
        "name": "info",
        "required": True,
        "many": True,
        "elements": [
            {
                "name": "language",
                "required": False,
            },
            {
                "name": "category",
                "required": True,
                "many": True,
            },
            {
                "name": "event",
                "required": True,
            },
            {
                "name": "responseType",
                "required": False,
                "many": True,
            },
            {
                "name": "urgency",
                "required": True,
            },
            {
                "name": "severity",
                "required": True,
            },
            {
                "name": "certainty",
                "required": True,
            },
            {
                "name": "audience",
                "required": False,
            },
            {
                "name": "eventCode",
                "required": False,
                "many": True,
                "elements": [
                    {
                        "name": "valueName",
                        "required": True,
                    },
                    {
                        "name": "value",
                        "required": True,
                    }
                ]
            },
            {
                "name": "effective",
                "required": False,
            },
            {
                "name": "onset",
                "required": False,
            },
            {
                "name": "expires",
                "required": False,
            },
            {
                "name": "senderName",
                "required": False,
            },
            {
                "name": "headline",
                "required": True,
            },
            {
                "name": "description",
                "required": True,
            },
            {
                "name": "instruction",
                "required": False,
            },
            {
                "name": "web",
                "required": False,
            },
            {
                "name": "contact",
                "required": False,
            },
            {
                "name": "parameter",
                "required": False,
                "many": True,
                "elements": [
                    {
                        "name": "valueName",
                        "required": True,
                    },
                    {
                        "name": "value",
                        "required": True,
                    }
                ]
            },
            {
                "name": "resource",
                "required": False,
                "many": True,
                "elements": [
                    {
                        "name": "resourceDesc",
                        "required": True,
                    },
                    {
                        "name": "mimeType",
                        "required": True,
                    },
                    {
                        "name": "size",
                        "required": False,
                    },
                    {
                        "name": "uri",
                        "required": False,
                    },
                    {
                        "name": "derefUri",
                        "required": False,
                    },
                    {
                        "name": "digest",
                        "required": False,
                    }
                ]
            },
            {
                "name": "area",
                "required": True,
                "many": True,
                "geo": True,
                "elements": [
                    {
                        "name": "areaDesc",
                        "required": True,
                    },
                    {
                        "name": "polygon",
                        "required": False,
                        "many": True,
                    },
                    {
                        "name": "circle",
                        "required": False,
                        "many": True,
                    },
                    {
                        "name": "geocode",
                        "required": False,
                        "many": True,
                        "elements": [
                            {
                                "name": "valueName",
                                "required": True,
                            },
                            {
                                "name": "value",
                                "required": True,
                            }
                        ]
                    },
                    {
                        "name": "altitude",
                        "required": False,
                    },
                    {
                        "name": "ceiling",
                        "required": False,
                    }
                ]
            }
        ]
    }
]


def extract_element_data(element, data, validate=True):
    """
    Extract element data.

    :param element: The element to extract.
    :param data: The data to extract from.
    :param validate: Whether to validate the data for required fields.
    :return: The extracted element data.
    """

    element_name = element["name"]
    element_data = data.get(element_name) or data.get(f"cap:{element_name}")

    if validate and element["required"] and not element_data:
        raise CAPImportError(f"Missing required element: {element_name}")

    if not element_data:
        return None

    if element.get("many"):
        if not isinstance(element_data, list):
            element_data = [element_data]

    if element.get("elements"):
        if isinstance(element_data, list):
            for i, item in enumerate(element_data):
                element_data[i] = {}
                for sub_element in element["elements"]:
                    sub_element_data = extract_element_data(sub_element, item, validate=validate)
                    sub_element_name = sub_element["name"]

                    if sub_element_data:
                        element_data[i][sub_element_name] = sub_element_data

                    if sub_element_name == "polygon":
                        if sub_element_data:
                            polygons = []
                            coordinates = []
                            for polygon in sub_element_data:
                                for point in polygon.split(" "):
                                    lat, lon = point.split(",")
                                    coordinates.append([float(lon), float(lat)])
                                polygons.append([coordinates])

                            if len(polygons) > 1:
                                geometry = {
                                    "type": "MultiPolygon",
                                    "coordinates": polygons
                                }
                            else:
                                geometry = {
                                    "type": "Polygon",
                                    "coordinates": polygons[0]
                                }
                            element_data[i]["geometry"] = geometry
        else:
            for sub_element in element["elements"]:
                sub_element_data = extract_element_data(sub_element, element_data, validate=validate)
                sub_element_name = sub_element["name"]

                if sub_element_data:
                    element_data[sub_element_name] = sub_element_data

    return element_data


def cap_xml_to_alert_data(cap_xml_string, validate=True):
    """
    Convert a CAP XML string to a GeoJSON FeatureCollection.

    :param cap_xml_string: A string containing a CAP XML document.
    :param validate: Whether to validate the CAP XML with the CAP schema for compulsory fields.
    :return: Alert data as a dictionary.
    """

    xml_dict = parse_xml_to_dict(cap_xml_string)

    alert_element_data = xml_dict.get("alert") or xml_dict.get("cap:alert")

    if not alert_element_data:
        raise CAPImportError("The loaded XML is not a valid CAP alert.")

    alert_data = {}

    for element in CAP_ALERT_ELEMENTS:
        element_name = element["name"]
        element_data = extract_element_data(element, alert_element_data, validate=validate)

        if element_data:
            alert_data[element_name] = element_data

    return alert_data
