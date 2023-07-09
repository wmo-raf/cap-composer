from rest_framework import generics

from capeditor.renderers import CustomXMLRenderer
from capeditor.serializers import AlertSerializer


class AlertList(generics.ListAPIView):
    serializer_class = AlertSerializer
    renderer_classes = (CustomXMLRenderer,)


class AlertDetail(generics.RetrieveAPIView):
    serializer_class = AlertSerializer
    renderer_classes = (CustomXMLRenderer,)

    lookup_field = "identifier"
