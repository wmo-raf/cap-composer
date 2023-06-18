from django.urls import path

from home.views import AlertList, AlertDetail

urlpatterns = [
    path('caps.xml', AlertList.as_view(), name="alert_list"),
    path("<uuid:identifier>.xml", AlertDetail.as_view(), name="alert_detail"),
]
