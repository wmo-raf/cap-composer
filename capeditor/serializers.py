from rest_framework import serializers
from .models import Alert, AlertArea, AlertInfo
from django.urls import reverse


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


class AlertGeocodeSerializer(serializers.ModelSerializer):

    class Meta:
        model = AlertArea
        fields = ['name', 'value']

class AlertAreaSerializer(serializers.ModelSerializer):
    geocode = serializers.SerializerMethodField()
    polygon = LatLonField(source="area")

    class Meta:
        model = AlertArea
        fields = ['area_desc', 'polygon', 'geocode', 'altitude', 'ceiling']
        # fields = '__all__'

    @staticmethod
    def get_geocode(obj):
        serializer = AlertAreaSerializer(obj.geocodes,  many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
      
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}

class AlertInfoSerializer(serializers.ModelSerializer):
    area = serializers.SerializerMethodField()

    class Meta:
        model = AlertInfo
        fields = ['language', 'category', 'event', 'urgency','severity', 'certainty', 'audience', 'effective', 'onset', 'expires', 'headline', 'description', 'instruction', 'web', 'contact', 'area',]
        # fields = '__all__'

    @staticmethod
    def get_area(obj):
        serializer = AlertAreaSerializer(obj.alert_areas,  many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
      
        return {k: v for k, v in representation.items() if v or v == 0 or v == False}


class AlertSerializer(serializers.ModelSerializer):

    info = serializers.SerializerMethodField()

    class Meta:
        model = Alert
        fields = ['identifier', 'sender', 'sent', 'status', 'message_type', 'scope', 'source', 'restriction', 'code', 'note', 'info']
        # fields = '__all__'
        # depth = 1

    
        
    @staticmethod
    def get_info(obj):
        serializer = AlertInfoSerializer(obj.alert_info,  many=True)
        return serializer.data


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Modify the XML tag name
        representation[f'msgType'] = representation.pop('message_type')
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

    