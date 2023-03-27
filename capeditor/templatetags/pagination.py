from django.template.defaultfilters import stringfilter
from django import template

register = template.Library()

@stringfilter
def remove_param(query_string, key):
    """
    Removes a given parameter from a query_string.

    For example, to delete page from "page=1&page=2&year=2020"

        {{ "page=1&page=2&year=2020"|remove_param:"page" }}

        returns year=2020

    """

    query_string = query_string.replace("&amp;", "&")

    params = query_string.split("&")

    url = ""

    for param in params:
        if param:
            v = param.split('=')
            if v[0] != key:
                url += param + "&"
    return url


register.filter(remove_param)