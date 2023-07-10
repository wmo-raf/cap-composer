from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks


@hooks.register("insert_editor_js")
def insert_editor_js():
    return format_html(
        '<script src="{}"></script>', static("capeditor/js/conditional_fields.js"),
    )


@hooks.register("register_icons")
def register_icons(icons):
    return icons + [
        'capeditor/icons/cap-alert.svg',
        'capeditor/icons/cap-alert-full.svg',
    ]
