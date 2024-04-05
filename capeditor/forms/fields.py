from django.contrib.gis.forms import GeometryField as BaseGeometryField
from django.contrib.gis.geos import GEOSException
from django.core.exceptions import ValidationError

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


class PolygonOrMultiPolygonField(BaseGeometryField):
    widget = PolygonWidget

    def clean(self, value):
        """
        Validate that the input value can be converted to a Geometry object
        and return it. Raise a ValidationError if the value cannot be
        instantiated as a Geometry.
        """
        geom = super(BaseGeometryField, self).clean(value)
        if geom is None:
            return geom

        # Ensuring that the geometry is of the correct type (indicated
        # using the OGC string label).
        val_geom_type = str(geom.geom_type).upper()

        ALLOWED_GEOM_TYPES = ["POLYGON", "MULTIPOLYGON"]

        if val_geom_type not in ALLOWED_GEOM_TYPES:
            raise ValidationError(
                self.error_messages["invalid_geom_type"], code="invalid_geom_type"
            )

        # Transforming the geometry if the SRID was set.
        if self.srid and self.srid != -1 and self.srid != geom.srid:
            try:
                geom.transform(self.srid)
            except GEOSException:
                raise ValidationError(
                    self.error_messages["transform_error"], code="transform_error"
                )

        return geom


class PolygonField(PolygonGeometryField):
    widget = PolygonWidget
