from django.shortcuts import render

from capeditor.forms.capimporter import CAPImportForm


def load_cap_alert(request):
    load_template_name = "capeditor/load_cap_alert.html"
    preview_template_name = "capeditor/preview_cap_alert.html"

    context = {}

    if request.method == "POST":
        form = CAPImportForm(request.POST, request.FILES)
        if form.is_valid():
            alert_data = form.cleaned_data["alert_data"]

            context.update({"alert_data": alert_data})

            return render(request, preview_template_name, context)

        else:
            context.update({"form": form})
            return render(request, template_name=load_template_name, context=context)

    form = CAPImportForm()
    context.update({"form": form})

    return render(request, load_template_name, context)
