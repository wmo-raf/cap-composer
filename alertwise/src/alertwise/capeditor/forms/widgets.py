import json
from unicodedata import category

from django.contrib.gis.forms import BaseGeometryWidget
from django.contrib.gis.geometry import json_regex
from django.forms import Textarea, Widget, TextInput, Media
from django.urls import reverse
from wagtail.telepath import register
from wagtail.widget_adapters import WidgetAdapter

from alertwise.capeditor.constants import WMO_HAZARD_EVENTS_TYPE_CHOICES
from alertwise.capeditor.oet_v1_2 import OASIS_EVENT_TERMS_AS_CHOICES


class BaseMapWidget(Widget):
    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        boundary_info_url = reverse("admin_boundary_info")
        context.update({
            "boundary_info_url": boundary_info_url
        })
        
        return context


class UNBoundaryWidgetMixin(Widget):
    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        un_geojson_url = reverse("un_boundary_geojson")
        context.update({
            "un_geojson_url": un_geojson_url
        })
        return context


class BasePolygonWidget(BaseGeometryWidget, BaseMapWidget):
    def serialize(self, value):
        return value.json if value else ""


class BoundaryPolygonWidget(BasePolygonWidget, UNBoundaryWidgetMixin):
    template_name = "capeditor/widgets/boundary_polygon_widget.html"
    map_srid = 4326
    
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__boundary-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}
        
        super().__init__(attrs=attrs)
    
    @property
    def media(self):
        css = {
            "all": [
                "capeditor/css/cap_detail_page.css",
                "capeditor/css/widget/boundary-widget.css",
            ]
        }
        
        js = [
            "capeditor/js/maplibre-gl.js",
            "capeditor/js/turf.min.js",
            "capeditor/js/widget/boundary-polygon-widget.js",
        ]
        
        return Media(js=js, css=css)


class BoundaryPolygonWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.BoundaryPolygonInput"
    
    class Media:
        js = [
            "capeditor/js/widget/boundary-polygon-widget-telepath.js",
        ]


register(BoundaryPolygonWidgetAdapter(), BoundaryPolygonWidget)


class PolygonWidget(BasePolygonWidget, UNBoundaryWidgetMixin):
    template_name = "capeditor/widgets/polygon_widget.html"
    map_srid = 4326
    
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__polygon-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}
        
        super().__init__(attrs=attrs)
    
    @property
    def media(self):
        return Media(
            css={
                "all": [
                    "capeditor/css/maplibre-gl.css",
                    "capeditor/css/mapbox-gl-draw.css",
                    "capeditor/css/widget/polygon-widget.css",
                ]
            },
            js=[
                "capeditor/js/maplibre-gl.js",
                "capeditor/js/mapbox-gl-draw.js",
                "capeditor/js/turf.min.js",
                "capeditor/js/widget/polygon-widget.js",
            ]
        )


class PolygonWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.PolygonInput"
    
    class Media:
        js = [
            "capeditor/js/widget/polygon-widget-telepath.js",
        ]


register(PolygonWidgetAdapter(), PolygonWidget)


class CircleWidget(BaseMapWidget, Textarea, UNBoundaryWidgetMixin):
    template_name = "capeditor/widgets/circle_widget.html"
    
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__circle-input",
        }
        
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(default_attrs)
    
    @property
    def media(self):
        return Media(
            css={
                "all": [
                    "capeditor/css/maplibre-gl.css",
                    "capeditor/css/widget/circle-widget.css",
                ]
            },
            js=[
                "capeditor/js/maplibre-gl.js",
                "capeditor/js/turf.min.js",
                "capeditor/js/widget/circle-widget.js",
            ]
        )


class CircleWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.CircleInput"
    
    class Media:
        js = [
            "capeditor/js/widget/circle-widget-telepath.js",
        ]


register(CircleWidgetAdapter(), CircleWidget)


class HazardEventTypeWidget(TextInput):
    template_name = "capeditor/widgets/hazard_event_type_widget.html"
    
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {}
        
        if attrs:
            default_attrs.update(attrs)
        
        super().__init__(default_attrs)
    
    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs['data-controller'] = 'hazard-event-type-widget'
        
        return attrs
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        
        options = []
        
        for choice in WMO_HAZARD_EVENTS_TYPE_CHOICES:
            options.append({
                "value": choice[0],
                "label": str(choice[1]),
            })
        
        context["widget"].update({
            "event_type_list": options
        })
        
        return context
    
    @property
    def media(self):
        return Media(
            js=[
                "capeditor/js/widget/hazard-event-type-widget.js",
                "capeditor/js/widget/hazard-event-type-widget-controller.js",
            ]
        )


class MultiPolygonWidget(BaseGeometryWidget, BaseMapWidget, UNBoundaryWidgetMixin):
    template_name = "capeditor/widgets/multipolygon_widget.html"
    map_srid = 4326
    
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__multipolygon-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}
        
        super().__init__(attrs=attrs)
    
    def serialize(self, value):
        return value.json if value else ""
    
    def deserialize(self, value):
        geom = super().deserialize(value)
        # GeoJSON assumes WGS84 (4326). Use the map's SRID instead.
        if geom and json_regex.match(value) and self.map_srid != 4326:
            geom.srid = self.map_srid
        return geom
    
    @property
    def media(self):
        return Media(
            css={
                "all": [
                    "capeditor/css/maplibre-gl.css",
                    "capeditor/css/mapbox-gl-draw.css",
                    "capeditor/css/widget/multipolygon-widget.css",
                ]
            },
            js=[
                "capeditor/js/maplibre-gl.js",
                "capeditor/js/mapbox-gl-draw.js",
                "capeditor/js/turf.min.js",
                "capeditor/js/widget/multipolygon-widget.js",
            ]
        )


class GeojsonFileLoaderWidget(BaseGeometryWidget, BaseMapWidget):
    template_name = "capeditor/widgets/geojson_file_loader_widget.html"
    
    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__polygon-draw-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}
        
        super().__init__(attrs=attrs)
    
    def serialize(self, value):
        return value.json if value else ""
    
    def deserialize(self, value):
        geom = super().deserialize(value)
        # GeoJSON assumes WGS84 (4326). Use the map's SRID instead.
        if geom and json_regex.match(value) and self.map_srid != 4326:
            geom.srid = self.map_srid
        return geom
    
    @property
    def media(self):
        css = {
            "all": [
                "capeditor/css/maplibre-gl.css",
                "capeditor/css/widget/geojson-file-loader-widget.css",
            ]
        }
        js = [
            "capeditor/js/maplibre-gl.js",
            "capeditor/js/turf.min.js",
            "capeditor/js/widget/geojson-file-loader-widget.js",
        ]
        
        return Media(js=js, css=css)


class EventCodeWidget(Textarea):
    template_name = 'capeditor/widgets/event_code_select_widget.html'
    
    def build_attrs(self, *args, **kwargs):
        attrs = super().build_attrs(*args, **kwargs)
        attrs['data-controller'] = 'event-code'
        
        return attrs
    
    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        
        event_term_choices = OASIS_EVENT_TERMS_AS_CHOICES
        choices = [{"value": value, "label": label, "cats": categories} for value, label, categories in
                   event_term_choices]
        context['choices'] = json.dumps(choices)
        return context
    
    @property
    def media(self):
        return Media(
            js=[
                "capeditor/js/widget/event-code-widget.js",
                "capeditor/js/widget/event-code-widget-controller.js",
            ]
        )
