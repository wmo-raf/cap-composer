import io

from django.core.files.base import ContentFile
from staticmap import StaticMap, Polygon
from wagtail.images import get_image_model

from alertwise.capeditor.constants import SEVERITY_MAPPING


def create_alert_area_image(
        alert_id,
        width=400,
        height=400,
        base_map_url_template='https://b.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'):
    from alertwise.cap.models import CapAlertPage
    
    cap_alert = CapAlertPage.objects.get(pk=alert_id)
    
    polygons = []
    for info in cap_alert.info:
        severity = SEVERITY_MAPPING[info.value.get("severity")]
        if info.value.area:
            for area in info.value.area:
                area_polygons = area.get("polygons")
                if area_polygons:
                    for polygon in area_polygons:
                        polygons.append({
                            "polygon": polygon,
                            "fill_color": severity.get("color"),
                            "outline_color": severity.get("border_color")
                        })
    
    m = StaticMap(
        width=width,
        height=height,
        padding_x=0,
        padding_y=0,
        url_template=base_map_url_template,
    )
    
    for polygon_obj in polygons:
        polygon = polygon_obj.get("polygon")
        fill_color = polygon_obj.get("fill_color")
        outline_color = polygon_obj.get("outline_color")
        
        polygon_strings = polygon.strip().split(" ")
        polygon_coords = [[float(lat), float(lon)] for lon, lat in (point.split(',') for point in polygon_strings)]
        
        if polygon_coords[0] != polygon_coords[-1]:
            polygon_coords.append(polygon_coords[0])
        
        s_polygon = Polygon(polygon_coords, fill_color=fill_color, outline_color=outline_color, simplify=True)
        m.add_polygon(s_polygon)
    
    buffer = io.BytesIO()
    m.render().save(buffer, format="PNG")
    
    filename = f"{cap_alert.slug}_{cap_alert.last_published_at.strftime('%s')}_map.png"
    image_title = f"{cap_alert.sent.strftime('%Y-%m-%d-%H-%M')} - Alert Area Map"
    
    area_image = get_image_model().objects.create(
        title=image_title,
        file=ContentFile(buffer.getvalue(), name=filename)
    )
    
    return area_image
