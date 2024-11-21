from importlib import import_module

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_object_or_none(model_class, **kwargs):
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        return None


def get_celery_app():
    """
    Dynamically imports the Celery app defined in settings.
    """
    
    CELERY_APP = getattr(settings, "CELERY_APP", None)
    
    if not CELERY_APP:
        raise ImproperlyConfigured("CELERY_APP is not defined in your settings")
    
    module_path, app_name = CELERY_APP.split(":")
    module = import_module(module_path)
    return getattr(module, app_name)