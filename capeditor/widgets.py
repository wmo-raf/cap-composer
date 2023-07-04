from django.contrib.gis.forms import BaseGeometryWidget
from wagtail.telepath import register
from wagtail.utils.widgets import WidgetWithScript
from wagtail.widget_adapters import WidgetAdapter


class PolygonWidget(WidgetWithScript, BaseGeometryWidget):
    template_name = "capeditor/widgets/polygon_widget.html"
    map_srid = 4326

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
                "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.css",
                "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.4.2/mapbox-gl-draw.css",
                "capeditor/css/polygon-widget.css",
            ]
        }
        js = [
            "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.js",
            "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.4.2/mapbox-gl-draw.js",
            "https://api.tiles.mapbox.com/mapbox.js/plugins/turf/v3.0.11/turf.min.js",
            "capeditor/js/polygon-widget-maplibre.js",
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
