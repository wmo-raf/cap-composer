from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response

from rest_framework import generics,renderers
from .models import Alert
from .serializers import AlertSerializer
from .renderers import CustomXMLRenderer
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt


class AlertList(generics.ListAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    renderer_classes = (CustomXMLRenderer,)

class AlertDetail(generics.RetrieveAPIView):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    renderer_classes = (CustomXMLRenderer,)
    lookup_field = 'identifier'

    # def get(self, request, format=None):
    #     pages = Alert.objects.all()
    #     serializer = AlertSerializer(pages, many=True)
    #     return Response(serializer.data)


# @api_view(["GET"])
# def get_alert_by_id(request, identifier):
#     alert = get_object_or_404(Alert, identifier=identifier)
#     alert_serializer = AlertSerializer(alert)

#     return JsonResponse(alert_serializer.data, safe=False)