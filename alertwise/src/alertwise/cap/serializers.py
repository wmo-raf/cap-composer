from alertwise.capeditor.serializers import AlertSerializer as BaseAlertSerializer

from .models import CapAlertPage


class AlertSerializer(BaseAlertSerializer):
    class Meta(BaseAlertSerializer.Meta):
        model = CapAlertPage
