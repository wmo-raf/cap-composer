from django.http import JsonResponse
from django.shortcuts import render, redirect
from wagtail import hooks

from alertwise.capeditor.forms.capimporter import CAPLoadForm, CAPImportForm
from .models import CapSetting


def load_cap_alert(request):
    load_template_name = "capeditor/load_cap_alert.html"
    preview_template_name = "capeditor/preview_cap_alert.html"
    
    context = {}
    
    if request.method == "POST":
        form = CAPLoadForm(request.POST, request.FILES)
        if form.is_valid():
            alert_data = form.cleaned_data["alert_data"]
            form = CAPImportForm(initial={"alert_data": alert_data})
            context.update({
                "alert_data": alert_data,
                "form": form,
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
            
            # run hook to import alert
            for fn in hooks.get_hooks("before_import_cap_alert"):
                result = fn(request, alert_data)
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
