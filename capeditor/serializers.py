from rest_framework import serializers
from capeditor.models import Alert, AlertArea, AlertInfo,AlertGeocode,AlertResponseType, AlertAddress, AlertReference, AlertResource
from django.urls import reverse
import datetime
import pytz

def parseTZ(date_str):
    dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    dt = dt.replace(tzinfo=pytz.UTC)
    date_str = dt.strftime("%Y-%m-%dT%H:%M:%S%z")
    date_str = date_str[:-2] + ':' + date_str[-2:]

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
        model = AlertAddress
        fields = ['address']

class AlertResponseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AlertResponseType
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
        model = AlertGeocode
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
        model = AlertResource
        fields = ['resourceDesc', 'uri', 'digest', 'size', 'mimeType']

class AlertAreaSerializer(serializers.ModelSerializer):
    geocode = serializers.SerializerMethodField()
    polygon = LatLonField(source="area")

    class Meta:
        model = AlertArea
        fields = ['areaDesc', 'polygon', 'geocode', 'altitude', 'ceiling']
        # fields = '__all__'

    @staticmethod
    def get_geocode(obj):
        serializer = AlertGeocodeSerializer(obj.geocodes,  many=True)
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
        model = AlertInfo
        fields = ['language', 'category', 'event','responseType', 'urgency','severity', 'certainty', 'audience', 'effective', 'onset', 'expires', 'headline', 'description', 'instruction', 'web', 'contact', 'area','resource']
        # fields = '__all__'


    @staticmethod
    def get_resource(obj):
        serializer = AlertResourceSerializer(obj.resources,  many=True)
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
        serializer = AlertAreaSerializer(obj.alert_areas,  many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['description'] = str(representation['description'])
        representation['effective'] = parseTZ(representation['effective'])
        representation['onset'] = parseTZ(representation['onset'])
        representation['expires'] = parseTZ(representation['expires'])

                
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}

class AlertReferenceSerializer(serializers.ModelSerializer):
    alerts = serializers.SerializerMethodField()
    class Meta:
        model = AlertReference
        fields = ['alerts']

    @staticmethod
    def get_alerts(obj):
        serializer = AlertSerializer(obj.ref_alert)

        data = serializer.data        

        return f"{data['sender']},{data['identifier']},{data['sent']}"

class AlertSerializer(serializers.ModelSerializer):

    info = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()
    references = serializers.SerializerMethodField()
    class Meta:
        model = Alert
        fields = ['identifier', 'sender', 'sent', 'status', 'msgType', 'scope', 'source', 'restriction', 'code', 'note', 'addresses', 'references','info']
        # fields = '__all__'
        # depth = 1
        
    @staticmethod
    def get_info(obj):
        serializer = AlertInfoSerializer(obj.alert_info,  many=True)
        return serializer.data

    @staticmethod
    def get_addresses(obj):
        serializer = AlertAddressSerializer(obj.addresses, many = True)
        address_ls = []

        if serializer.data:
            for data in serializer.data:
                if data['address']:
                    address_ls.append(data['address'])

            return ' '.join(address_ls)
        
        return None

    @staticmethod
    def get_references(obj):
        serializer = AlertReferenceSerializer(obj.references, many = True)

        reference_ls =[]
        if serializer.data:
            for data in serializer.data:
                if data['alerts']:
                    reference_ls.append(data['alerts'])

            return ' '.join(reference_ls)

        return serializer.data


    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['sent'] = parseTZ(representation['sent'])
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
        if representation[f'msgType'] == 'Update' or representation[f'msgType'] == 'Cancel'  or representation[f'msgType'] == 'Ack':
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

    