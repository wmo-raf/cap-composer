from adminboundarymanager.models import AdminBoundarySettings
from django.contrib.gis.forms import BaseGeometryWidget
from django.contrib.gis.geos import GEOSGeometry
from django.forms import Textarea, Widget
from django.urls import reverse
from shapely import wkt, Polygon
from wagtail.models import Site
from wagtail.telepath import register
from wagtail.utils.widgets import WidgetWithScript
from wagtail.widget_adapters import WidgetAdapter


class BaseMapWidget(Widget):
    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)

        try:
            site = Site.objects.get(is_default_site=True)
            abm_settings = AdminBoundarySettings.for_site(site)
            boundary_tiles_url = abm_settings.boundary_tiles_url
            boundary_tiles_url = site.root_url + boundary_tiles_url

            boundary_detail_url = reverse("admin_boundary_detail", args=[0]).replace("/0", "")
            boundary_detail_url = site.root_url + boundary_detail_url

            context.update({
                "boundary_tiles_url": boundary_tiles_url,
                "boundary_detail_url": boundary_detail_url,
                "country_bounds": abm_settings.combined_countries_bounds
            })

        except Exception:
            pass

        return context


class BasePolygonWidget(BaseGeometryWidget, BaseMapWidget):
    def serialize(self, value):
        return value.json if value else ""

    def deserialize(self, value):
        geom = super().deserialize(value)
        tolerance = 0.05

        if geom.geom_type != "Polygon":
            # try to get the smallest Polygon that contains all the geometries in the MultiPolygon.
            geom = geom.unary_union

        # first simplification
        geom = geom.simplify(tolerance)

        # still not a Polygon. Simplify with incrementing tolerance until we have a polygon
        while geom.geom_type != "Polygon":
            tolerance *= 2
            geom = geom.simplify(tolerance)

        # check for holes and close if any
        shape_geom = wkt.loads(geom.wkt)
        if shape_geom.interiors:
            polygon_no_holes = Polygon(shape_geom.exterior)
            geom = GEOSGeometry(polygon_no_holes.wkt)

        return geom


class BoundaryPolygonWidget(WidgetWithScript, BasePolygonWidget):
    template_name = "capeditor/widgets/boundary_polygon_widget.html"
    map_srid = 4326

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__boundary-input",
        }
        attrs = attrs or {}
        attrs = {**default_attrs, **attrs}

        super().__init__(attrs=attrs)

    class Media:
        css = {
            "all": [
                "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.css",
                "capeditor/css/widget/boundary-widget.css",
            ]
        }
        js = [
            "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.js",
            "https://unpkg.com/@turf/turf/turf.min.js",
            "capeditor/js/widget/boundary-polygon-widget.js",
        ]


class BoundaryPolygonWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.BoundaryPolygonInput"

    class Media:
        js = [
            "capeditor/js/widget/boundary-polygon-widget-telepath.js",
        ]


register(BoundaryPolygonWidgetAdapter(), BoundaryPolygonWidget)


class PolygonWidget(WidgetWithScript, BasePolygonWidget):
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
                "capeditor/css/widget/polygon-widget.css",
            ]
        }
        js = [
            "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.js",
            "https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-draw/v1.4.2/mapbox-gl-draw.js",
            "https://unpkg.com/@turf/turf/turf.min.js",
            "capeditor/js/widget/polygon-widget.js",
        ]


class PolygonWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.PolygonInput"

    class Media:
        js = [
            "capeditor/js/widget/polygon-widget-telepath.js",
        ]


register(PolygonWidgetAdapter(), PolygonWidget)


class CircleWidget(WidgetWithScript, BaseMapWidget, Textarea):
    template_name = "capeditor/widgets/circle_widget.html"

    def __init__(self, attrs=None):
        default_attrs = {
            "class": "capeditor-widget__circle-input",
        }

        if attrs:
            default_attrs.update(attrs)

        super().__init__(default_attrs)

    class Media:
        css = {
            "all": [
                "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.css",
                "capeditor/css/widget/circle-widget.css",
            ]
        }
        js = [
            "https://unpkg.com/maplibre-gl@2.1.1/dist/maplibre-gl.js",
            "https://unpkg.com/@turf/turf/turf.min.js",
            "capeditor/js/widget/circle-widget.js",
        ]


class CircleWidgetAdapter(WidgetAdapter):
    js_constructor = "capeditor.widgets.CircleInput"

    class Media:
        js = [
            "capeditor/js/widget/circle-widget-telepath.js",
        ]


register(CircleWidgetAdapter(), CircleWidget)
