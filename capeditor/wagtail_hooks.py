
from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static
from capeditor.models import Alert
from wagtail.contrib.modeladmin.options import (
    ModelAdmin, 
    modeladmin_register,
    ModelAdminGroup
)

@hooks.register("insert_editor_js")
def insert_editor_js():
    return format_html(
        '<script src="{}"></script>',static("js/hide_attributes.js"),
    )


@hooks.register("insert_global_admin_css")
def insert_global_admin_css():
    return format_html(
        '<link rel="stylesheet" type="text/css" href="{}">',
        static("css/admin.css"),
    )

class CAPAdmin(ModelAdmin):
    model = Alert
    menu_label = 'CAP Alerts'
    menu_icon = 'cog'
    menu_order = 200 
    add_to_settings_menu = False
    exclude_from_explorer = False

modeladmin_register(CAPAdmin)