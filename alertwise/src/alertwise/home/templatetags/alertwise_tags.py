from django import template
from django.conf import settings
from wagtail.models import Site

register = template.Library()


@register.filter
def django_settings(value):
    return getattr(settings, value, None)


@register.simple_tag
def wagtail_default_site():
    """
    Returns the default Site object
    """
    
    return Site.objects.get(is_default_site=True)
