from django.contrib.gis.forms import GeometryField as BaseGeometryField

from .widgets import PolygonWidget, BoundaryPolygonWidget


class MultiPolygonGeometryField(BaseGeometryField):
    geom_type = 'MULTIPOLYGON'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.geom_type = self.geom_type


class PolygonGeometryField(BaseGeometryField):
    geom_type = 'POLYGON'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget.geom_type = self.geom_type


class BoundaryMultiPolygonField(MultiPolygonGeometryField):
    widget = BoundaryPolygonWidget


class MultiPolygonField(MultiPolygonGeometryField):
    widget = PolygonWidget


class PolygonField(PolygonGeometryField):
    widget = PolygonWidget
