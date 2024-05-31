from django.urls import path

from home.views import AlertList, AlertDetail

urlpatterns = [
    path('api/cap/feed.xml', AlertList.as_view(), name="cap_alert_feed"),
    path("api/cap/<uuid:guid>.xml", AlertDetail.as_view(), name="cap_alert_detail"),
]
