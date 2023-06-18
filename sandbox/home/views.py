from rest_framework import generics

from capeditor.renderers import CustomXMLRenderer
from capeditor.serializers import AlertSerializer
from home.models import CapAlertPage


class AlertList(generics.ListAPIView):
    serializer_class = AlertSerializer
    serializer_class.Meta.model = CapAlertPage

    renderer_classes = (CustomXMLRenderer,)
    queryset = CapAlertPage.objects.live()


class AlertDetail(generics.RetrieveAPIView):
    serializer_class = AlertSerializer
    serializer_class.Meta.model = CapAlertPage

    renderer_classes = (CustomXMLRenderer,)
    queryset = CapAlertPage.objects.live()

    lookup_field = "identifier"
