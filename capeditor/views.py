from django.shortcuts import render, redirect
from wagtail import hooks

from capeditor.forms.capimporter import CAPLoadForm, CAPImportForm


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
