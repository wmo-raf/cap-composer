from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.documents import urls as wagtaildocs_urls

from alertwise.config.views import humans

handler500 = 'alertwise.config.views.handler500'

ADMIN_URL_PATH = getattr(settings, "ADMIN_URL_PATH", None)
DJANGO_ADMIN_URL_PATH = getattr(settings, "DJANGO_ADMIN_URL_PATH", None)

urlpatterns = [
    path("documents/", include(wagtaildocs_urls)),
    path("", include("alertwise.cap.urls")),
    path("", include("adminboundarymanager.urls")),
    path("sitemap.xml", sitemap),
    path("humans.txt", humans),
]

if ADMIN_URL_PATH:
    ADMIN_URL_PATH = ADMIN_URL_PATH.strip("/")
    urlpatterns += path(f"{ADMIN_URL_PATH}/", include(wagtailadmin_urls), name='admin'),

if DJANGO_ADMIN_URL_PATH:
    DJANGO_ADMIN_URL_PATH = DJANGO_ADMIN_URL_PATH.strip("/")
    urlpatterns += path(f"{DJANGO_ADMIN_URL_PATH}/", admin.site.urls, name='django-admin'),

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    
    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
