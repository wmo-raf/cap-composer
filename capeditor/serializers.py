import pytz
from dateutil.parser import isoparse
from rest_framework import serializers
from wagtail.api.v2.utils import get_full_url

from capeditor.constants import CAP_MESSAGE_ORDER_SEQUENCE
from capeditor.utils import order_dict_by_keys


def parse_tz(date_str):
    dt = isoparse(date_str)
    # check if we have timezone info
    if dt.tzinfo:
        # check if timezone is equal to UTC, and replace '+' with '-' to match CAP Protocol time formats
        if dt.utcoffset().total_seconds() == 0:
            date_str = dt.isoformat().replace("+", "-")
        else:
            date_str = dt.isoformat()
    # NO timezone. Assume is UTC
    else:
        date_str = dt.replace(tzinfo=pytz.UTC).isoformat().replace("+", "-")

    return date_str


class AlertSerializer(serializers.ModelSerializer):
    addresses = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    info = serializers.SerializerMethodField()
    incidents = serializers.SerializerMethodField()
    identifier = serializers.SerializerMethodField()

    class Meta:
        fields = [
            "identifier",
            "sender",
            "sent",
            "status",
            "msgType",
            "source",
            "scope",
            "restriction",
            "addresses",
            "code",
            "note",
            "references",
            "incidents",
            "info",
        ]

    def get_identifier(self, obj):
        if hasattr(obj, 'identifier'):
            return obj.identifier
        return obj.guid

    def get_info(self, obj):
        request = self.context.get("request")
        info_values = []

        for info in obj.info:
            info_obj = info.block.get_api_representation(info.value)
            if info.value.resource:
                resources = []
                for resource in info.value.resource:
                    if resource.get("type") == "doc":
                        resource["uri"] = get_full_url(request, resource.get("uri"))
                    resource.pop("type")
                    # order resource according to CAP_MESSAGE_ORDER_SEQUENCE
                    resource_obj = order_dict_by_keys(resource, CAP_MESSAGE_ORDER_SEQUENCE.get("resource"))
                    resources.append(resource_obj)
                info_obj["resource"] = resources

            # assign full url
            info_obj["web"] = obj.get_full_url(request)
            for field in list(info_obj):
                if not info_obj[field]:
                    info_obj.pop(field)
            area_values = []

            # format responseTypes
            if info_obj.get("responseType"):
                response_types = []
                for response_type in info_obj.get("responseType"):
                    response_types.append(response_type.get("response_type"))
                info_obj["responseType"] = response_types

            # format area
            if info.value.area:
                areas = []
                for area in info.value.area:
                    area_obj = order_dict_by_keys(area, CAP_MESSAGE_ORDER_SEQUENCE.get("area"))
                    areas.append(area_obj)
                info_obj["area"] = areas

            # order according to CAP_MESSAGE_ORDER_SEQUENCE
            info_obj = order_dict_by_keys(info_obj, CAP_MESSAGE_ORDER_SEQUENCE.get("info"))

            info_values.append(info_obj)

        return info_values

    @staticmethod
    def get_addresses(obj):
        address_values = []
        for address in obj.addresses:
            address_obj = address.block.get_api_representation(address.value)
            address_values.append(address_obj.get("address"))

        if address_values:
            return " ".join(address_values)

        return None

    @staticmethod
    def get_references(obj):
        reference_values = []
        for reference in obj.references:
            if reference.value.ref_alert_identifier:
                reference_values.append(reference.value.ref_alert_identifier)
        if reference_values:
            return " ".join(reference_values)
        return None

    @staticmethod
    def get_incidents(obj):
        incident_values = []
        for incident in obj.incidents:
            incident_obj = incident.block.get_api_representation(incident.value)
            incident_val = incident_obj.get('incident')
            incident_values.append(f'"{incident_val}"')

        if incident_values:
            return " ".join(incident_values)

        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['sent'] = parse_tz(representation['sent'])

        # check for scope condition
        if representation[f'scope'] == 'Restricted':
            representation[f'addresses'] = None
        elif representation[f'scope'] == 'Private':
            representation[f'restriction'] = None
        elif representation[f'scope'] == 'Public':
            representation[f'restriction'] = None
            representation[f'addresses'] = None

        # check message type
        if representation['msgType'] == 'Update' or representation['msgType'] == 'Cancel' or \
                representation['msgType'] == 'Ack':
            representation[f'note'] = None
        elif representation[f'msgType'] == 'Alert':
            representation[f'note'] = None
            representation[f'references'] = None

        return {k: v for k, v in representation.items() if v or v == 0 or v is False}
