import json

from django import forms
from django.contrib.gis.forms import BaseGeometryWidget
from django.forms import widgets
from django.utils.functional import cached_property
from wagtail.telepath import register
from wagtail.utils.widgets import WidgetWithScript
from wagtail.widget_adapters import WidgetAdapter


class BasemapPolygonWidget(forms.HiddenInput):
    template_name = "capeditor/widgets/basemap_polygon.html"

    @cached_property
    def media(self):
        return forms.Media(
            css={
                "all": (
                    "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css",
                    "https://unpkg.com/leaflet@1.7.1/dist/leaflet.css",

                )
            },
            js=(
                "https://unpkg.com/leaflet@1.7.1/dist/leaflet.js",
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js",
                "https://unpkg.com/togeojson@0.16.0",
                "https://unpkg.com/leaflet-filelayer@1.2.0",
                "https://kit.fontawesome.com/db8ac3c257.js"
            ),
        )

    def get_context(self, name, value, attrs=None):
        context = super().get_context(name, value, attrs)
        context['map_id'] = f'map-{name}'

        return context


class PolygonWidget(WidgetWithScript, BaseGeometryWidget):
    template_name = "capeditor/widgets/polygon_widget.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__polygon-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}
        super().__init__(attrs=attrs)

    class Media:
        css = {
            "all": [
                "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css",
                "capeditor/css/polygon-widget.css",
            ]
        }
        js = [
            "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
            "https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js",
            "https://unpkg.com/togeojson@0.16.0",
            "https://unpkg.com/leaflet-filelayer@1.2.0",
            "capeditor/js/polygon-widget.js",
        ]

    def serialize(self, value):
        return value.json if value else ""


class PolygonWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.PolygonInput"

    class Media:
        js = [
            "capeditor/js/polygon-widget-telepath.js",
        ]


register(PolygonWidgetAdapter(), PolygonWidget)
