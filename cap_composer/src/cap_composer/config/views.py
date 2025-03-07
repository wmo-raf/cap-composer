from django.shortcuts import render


def handler500(request):
    context = {}
    response = render(request, "500.html", context=context)
    response.status_code = 500
    return response


def humans(request):
    return render(request, "humans.txt", context={}, content_type="text/plain; charset=utf-8", )
