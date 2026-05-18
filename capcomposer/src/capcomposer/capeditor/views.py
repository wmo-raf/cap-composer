import json
import os
import tempfile

from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST
from wagtail import hooks

from capcomposer.capeditor.forms.capimporter import CAPLoadForm, CAPImportForm
from .models import CapSetting


def load_cap_alert(request):
    load_template_name = "capeditor/load_cap_alert.html"
    preview_template_name = "capeditor/preview_cap_alert.html"
    
    context = {}
    
    if request.method == "POST":
        form = CAPLoadForm(request.POST, request.FILES)
        if form.is_valid():
            alert_data = form.cleaned_data["alert_data"]
            include_guid = form.cleaned_data["include_guid"]
            
            form = CAPImportForm(initial={"alert_data": alert_data, "include_guid": include_guid})
            context.update({
                "alert_data": alert_data,
                "form": form,
                "include_guid": include_guid,
            })
            
            return render(request, preview_template_name, context)
        
        else:
            context.update({"form": form})
            return render(request, template_name=load_template_name, context=context)
    
    form = CAPLoadForm()
    context.update({"form": form})
    
    return render(request, load_template_name, context)


def import_cap_alert(request):
    if request.method == "POST":
        form = CAPImportForm(request.POST)
        if form.is_valid():
            alert_data = form.cleaned_data["alert_data"]
            include_guid = form.cleaned_data["include_guid"]
            
            # run hook to import alert
            for fn in hooks.get_hooks("before_import_cap_alert"):
                result = fn(request, alert_data, include_guid)
                if hasattr(result, "status_code"):
                    return result
            
            return redirect("load_cap_alert")
        else:
            return redirect("load_cap_alert")
    
    return redirect("load_cap_alert")


def get_un_boundary_geojson(request):
    cap_settings = CapSetting.for_request(request)
    un_country_boundary_geojson = cap_settings.un_country_boundary_geojson
    if not un_country_boundary_geojson:
        return JsonResponse({})
    
    return JsonResponse(un_country_boundary_geojson)


def convert_area_file(request):
    """Accept a GeoJSON or shapefile ZIP and return a MultiPolygon GeoJSON geometry."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
        return JsonResponse({'error': 'No file provided'}, status=400)
    
    filename = uploaded_file.name.lower()
    
    try:
        if filename.endswith('.geojson') or filename.endswith('.json'):
            content = uploaded_file.read().decode('utf-8')
            data = json.loads(content)
            geom = _extract_multipolygon_from_geojson(data)
            return JsonResponse({'geometry': geom})
        
        elif filename.endswith('.zip'):
            import fiona
            from fiona.transform import transform_geom
            
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                for chunk in uploaded_file.chunks():
                    tmp.write(chunk)
                tmp_path = tmp.name
            
            try:
                geometries = []
                with fiona.open(f'zip://{tmp_path}') as src:
                    src_crs = src.crs
                    need_reproject = (
                            src_crs is not None and
                            src_crs.to_epsg() != 4326
                    )
                    
                    for feature in src:
                        if feature.geometry is None:
                            continue
                        geom = dict(feature.geometry)
                        if need_reproject:
                            geom = dict(transform_geom(src_crs, 'EPSG:4326', geom))
                        if geom['type'] == 'Polygon':
                            geometries.append(geom['coordinates'])
                        elif geom['type'] == 'MultiPolygon':
                            geometries.extend(geom['coordinates'])
                
                if not geometries:
                    return JsonResponse(
                        {'error': 'No polygon geometries found in the shapefile'},
                        status=400,
                    )
                
                return JsonResponse({
                    'geometry': {'type': 'MultiPolygon', 'coordinates': geometries}
                })
            finally:
                os.unlink(tmp_path)
        
        else:
            return JsonResponse(
                {'error': 'Unsupported file format. Please upload .geojson, .json, or .zip (shapefile)'},
                status=400,
            )
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def _extract_multipolygon_from_geojson(data):
    geom_type = data.get('type')
    
    if geom_type == 'FeatureCollection':
        features = data.get('features', [])
        if not features:
            raise ValueError('Empty FeatureCollection')
        all_coords = []
        for feature in features:
            geom = feature.get('geometry') or {}
            if geom.get('type') == 'Polygon':
                all_coords.append(geom['coordinates'])
            elif geom.get('type') == 'MultiPolygon':
                all_coords.extend(geom['coordinates'])
        if not all_coords:
            raise ValueError('No Polygon or MultiPolygon geometries found')
        return {'type': 'MultiPolygon', 'coordinates': all_coords}
    
    elif geom_type == 'Feature':
        return _ensure_multipolygon(data.get('geometry') or {})
    
    elif geom_type in ('Polygon', 'MultiPolygon'):
        return _ensure_multipolygon(data)
    
    else:
        raise ValueError(f'Unsupported GeoJSON type: {geom_type}')


def _ensure_multipolygon(geom):
    if geom.get('type') == 'Polygon':
        return {'type': 'MultiPolygon', 'coordinates': [geom['coordinates']]}
    elif geom.get('type') == 'MultiPolygon':
        return geom
    else:
        raise ValueError(f"Expected Polygon or MultiPolygon geometry, got {geom.get('type')}")


def map_widget_config(request):
    cap_setting = CapSetting.for_request(request)
    
    config = {
        "intersection_area_threshold": cap_setting.intersection_area_threshold if cap_setting else 1000,
    }
    
    return JsonResponse(config)


@require_POST
def translate_text(request):
    """Translate text fields to a target language using the configured translator service."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)
    
    texts = data.get('texts', {})
    target_language = data.get('target_language', '').strip()
    source_language = data.get('source_language', 'auto').strip() or 'auto'
    
    if not target_language or not isinstance(texts, dict):
        return JsonResponse({'error': 'Missing required fields'}, status=400)
    
    try:
        from django_deep_translator.utils import get_translator
        translator = get_translator()
    except Exception as e:
        return JsonResponse({'error': f'Translation service unavailable: {e}'}, status=503)
    
    translated = {}
    for key, text in texts.items():
        if text and isinstance(text, str) and text.strip():
            try:
                translated[key] = translator.translate_string(text, target_language, source_language)
            except Exception:
                translated[key] = text
        else:
            translated[key] = text
    
    return JsonResponse({'translated': translated})
