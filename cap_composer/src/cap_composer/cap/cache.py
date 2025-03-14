from django.core.cache import caches

from wagtailcache.settings import wagtailcache_settings

wagcache = caches[wagtailcache_settings.WAGTAIL_CACHE_BACKEND]
