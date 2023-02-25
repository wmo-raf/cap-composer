from django.urls import path,register_converter

from .views import AlertList,AlertDetail

class IdentifierConverter:
    regex = r'[A-Za-z0-9_-]+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

register_converter(IdentifierConverter, 'identifier')

urlpatterns = [
    path('caps.xml', AlertList.as_view()),
    path("<identifier:identifier>.xml", AlertDetail.as_view(), name="alert_by_id"),
]