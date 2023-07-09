from django.urls import path

from capeditor.views import AlertList, AlertDetail

urlpatterns = [
    path('caps.xml', AlertList.as_view()),
    path("<identifier:uuid>.xml", AlertDetail.as_view(), name="alert_by_id"),
]
