import pytz
from dateutil.parser import isoparse
from rest_framework import serializers
from shapely import wkt


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


class LatLonField(serializers.Field):
    def to_representation(self, value):
        # Check if the value is None or an empty string
        if not value:
            return None

        # Extract the latitude and longitude values from the polygon string
        polygon_str = str(value)
        polygon_str = polygon_str.replace('((', '(').replace('))', ')')

        start_index = polygon_str.find("(") + 1
        end_index = polygon_str.find(")")
        coords_str = polygon_str[start_index:end_index]
        lat_lon_pairs = coords_str.split(", ")

        lat_lon_ls = []
        for pair in lat_lon_pairs:
            lat_lon_ls.append(f'{pair.split(" ")[1]},{pair.split(" ")[0]}')

        # Return the latitude and longitude values as a dictionary
        return " ".join(lat_lon_ls)


class AlertAddressSerializer(serializers.ModelSerializer):
    # address_ls = AddressField(source="address")

    class Meta:
        fields = ['address']


class AlertResponseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['response_type']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Modify the XML tag name
        representation[f'responseType'] = representation.pop('response_type')
        # request = self.context.get('request')
        # if request:
        #     representation['link'] = self.get_link(instance)
        # Modify the XML output as needed
        # representation['other_field'] = 'some value'
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}


class AlertGeocodeSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['name', 'value']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Modify the XML tag name
        representation[f'valueName'] = representation.pop('name')
        # request = self.context.get('request')
        # if request:
        #     representation['link'] = self.get_link(instance)
        # Modify the XML output as needed
        # representation['other_field'] = 'some value'
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}


class AlertResourceSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['resourceDesc', 'uri', 'digest', 'size', 'mimeType']


class AlertAreaSerializer(serializers.ModelSerializer):
    geocode = serializers.SerializerMethodField()
    polygon = LatLonField(source="area")

    class Meta:
        fields = ['areaDesc', 'polygon', 'geocode', 'altitude', 'ceiling']
        # fields = '__all__'

    @staticmethod
    def get_geocode(obj):
        serializer = AlertGeocodeSerializer(obj.geocodes, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        return {k: v for k, v in representation.items() if v or v == 0 or v == False}


class AlertInfoSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()
    responseType = serializers.SerializerMethodField()
    description = serializers.CharField()
    resource = serializers.SerializerMethodField()

    class Meta:
        fields = ['language', 'category', 'event', 'responseType', 'urgency', 'severity', 'certainty', 'audience',
                  'effective', 'onset', 'expires', 'headline', 'description', 'instruction', 'web', 'contact', 'area',
                  'resource']
        # fields = '__all__'

    @staticmethod
    def get_resource(obj):
        serializer = AlertResourceSerializer(obj.resources, many=True)
        return serializer.data

    @staticmethod
    def get_responseType(obj):
        serializer = AlertResponseTypeSerializer(obj.response_types, many=True)
        resp_ls = []
        for resp in serializer.data:
            resp_ls.append(resp['responseType'])

        return resp_ls

    @staticmethod
    def get_area(obj):
        serializer = AlertAreaSerializer(obj.alert_areas, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['effective'] = parse_tz(representation['effective'])
        representation['onset'] = parse_tz(representation['onset'])
        representation['expires'] = parse_tz(representation['expires'])

        return {k: v for k, v in representation.items() if v or v == 0 or v == False}


class AlertReferenceSerializer(serializers.ModelSerializer):
    alerts = serializers.SerializerMethodField()

    class Meta:
        fields = ['alerts']

    @staticmethod
    def get_alerts(obj):
        serializer = AlertSerializer(obj.ref_alert)

        data = serializer.data

        return f"{data['sender']},{data['identifier']},{data['sent']}"


class AlertSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField()

    # addresses = serializers.SerializerMethodField()
    # references = serializers.SerializerMethodField()

    class Meta:
        fields = ['identifier', 'sender', 'sent', 'status', 'msgType', 'scope', 'source', 'restriction', 'code', 'note',
                  'info']

    def get_info(self, obj):
        request = self.context.get("request")
        info_values = []
        for info in obj.info:
            info_obj = info.block.get_api_representation(info.value)
            # assign full url
            info_obj["web"] = obj.get_full_url(request)
            for field in list(info_obj):
                if not info_obj[field]:
                    info_obj.pop(field)

            area_values = []
            if info_obj.get("area"):
                areas = info_obj.get("area")
                for area in areas:
                    shape = wkt.loads(area.get("polygon"))
                    if shape:
                        area_value = {
                            **area,
                            "polygon": " ".join(["{},{}".format(x, y) for x, y in list(shape.exterior.coords)])
                        }
                        for field in list(area_value):
                            if not area_value[field]:
                                area_value.pop(field)
                        area_values.append(area_value)
                info_obj["area"] = area_values

            info_values.append(info_obj)
        return info_values

    @staticmethod
    def get_addresses(obj):
        serializer = AlertAddressSerializer(obj.addresses, many=True)
        address_ls = []

        if serializer.data:
            for data in serializer.data:
                if data['address']:
                    address_ls.append(data['address'])

            return ' '.join(address_ls)

        return None

    @staticmethod
    def get_references(obj):
        serializer = AlertReferenceSerializer(obj.references, many=True)

        reference_ls = []
        if serializer.data:
            for data in serializer.data:
                if data['alerts']:
                    reference_ls.append(data['alerts'])

            return ' '.join(reference_ls)

        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['sent'] = parse_tz(representation['sent'])
        # Modify the XML tag name
        # representation[f'msgType'] = representation.pop('message_type')

        # check for scope condition
        if representation[f'scope'] == 'Restricted':
            representation[f'addresses'] = None
        elif representation[f'scope'] == 'Private':
            representation[f'restriction'] = None
        elif representation[f'scope'] == 'Public':
            representation[f'restriction'] = None
            representation[f'addresses'] = None

        # check message type 
        if representation[f'msgType'] == 'Update' or representation[f'msgType'] == 'Cancel' or representation[
            f'msgType'] == 'Ack':
            representation[f'note'] = None
        elif representation[f'msgType'] == 'Alert':
            representation[f'note'] = None
            representation[f'references'] = None

        # request = self.context.get('request')
        # if request:
        #     representation['link'] = self.get_link(instance)
        # Modify the XML output as needed
        # representation['other_field'] = 'some value'
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}

    # def get_link(self, obj):
    #     # define your custom URL generation logic here
    #     # the `obj` parameter is the object being serialized
    #     return reverse('alert_by_id', args=[obj.identifier])
