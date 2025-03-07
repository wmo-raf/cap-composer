from django.conf import settings
from django.contrib.auth.models import Permission
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _, gettext
from wagtail import hooks
from wagtail.actions.copy_page import CopyPageAction
from wagtail.admin import messages
from wagtail.admin.forms.pages import CopyForm
from wagtail.admin.menu import MenuItem, Menu
from wagtail.models import Page, Site
from wagtail_modeladmin.helpers import AdminURLHelper
from wagtail_modeladmin.helpers import (
    PagePermissionHelper,
    PermissionHelper,
    PageButtonHelper
)
from wagtail_modeladmin.menus import GroupMenuItem
from wagtail_modeladmin.options import (
    ModelAdmin,
    modeladmin_register,
    ModelAdminGroup
)

from alertwise.capeditor.models import CapSetting
from .models import (
    CapAlertPage,
    CapAlertListPage,
    CAPAlertWebhook,
    CAPAlertWebhookEvent,
    OtherCAPSettings,
    CAPAlertMQTTBroker,
    CAPAlertMQTTBrokerEvent,
    ExternalAlertFeed

)
from .utils import (
    create_draft_alert_from_alert_data
)


class CAPPagePermissionHelper(PagePermissionHelper):
    def user_can_edit_obj(self, user, obj):
        can_edit = super().user_can_edit_obj(user, obj)
        
        # allow editing if enabled from settings
        can_edit_cap = getattr(settings, "CAP_ALLOW_EDITING", False)
        if can_edit_cap:
            return True
        
        if obj.live and obj.status == "Actual":
            return False
        
        return can_edit
    
    def user_can_delete_obj(self, user, obj):
        can_delete = super().user_can_delete_obj(user, obj)
        
        if obj.live and obj.status == "Actual":
            return False
        
        return can_delete
    
    def user_can_unpublish_obj(self, user, obj):
        can_unpublish = super().user_can_unpublish_obj(user, obj)
        
        if obj.live and obj.status == "Actual":
            return False
        
        return can_unpublish


class CAPAlertPageButtonHelper(PageButtonHelper):
    def get_buttons_for_obj(self, obj, exclude=None, classnames_add=None, classnames_exclude=None):
        buttons = super().get_buttons_for_obj(obj, exclude, classnames_add, classnames_exclude)
        
        classnames = self.edit_button_classnames + classnames_add
        cn = self.finalise_classname(classnames, classnames_exclude)
        
        if obj.is_published_publicly:
            live_button = {
                "url": obj.get_full_url(),
                "label": _("LIVE"),
                "classname": cn,
                "title": _("Visit the live page")
            }
            
            buttons = [live_button] + buttons
        
        return buttons


class CAPAdmin(ModelAdmin):
    model = CapAlertPage
    menu_label = _('Alerts')
    menu_icon = 'list-ul'
    menu_order = 200
    add_to_settings_menu = False
    exclude_from_explorer = False
    permission_helper_class = CAPPagePermissionHelper
    button_helper_class = CAPAlertPageButtonHelper
    list_display_add_buttons = "__str__"
    list_filter = ("live", "msgType", "sent")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # self.list_display = ["publish_status"] + list(self.list_display)
        
        # self.publish_status.__func__.short_description = _('Publish Status')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        if self.is_pagemodel:
            site = Site.find_for_request(request)
            root_page = site.root_page
            
            # filter only alerts that are children of this specific CapAlertListPage
            if isinstance(root_page.specific, CapAlertListPage):
                qs = qs.child_of(root_page.specific)
        
        return qs
    
    # def publish_status(self, obj):
    #     if obj.live:
    #         return format_html(
    #             '<span class="w-status w-status--primary">{}</span>',
    #             _("Live"),
    #         )
    #
    #     if obj.latest_revision and obj.latest_revision.submitted_for_moderation:
    #         return format_html(
    #             '<span class="w-status">{}</span>',
    #             _("In moderation"),
    #         )
    #
    #     return format_html(
    #         '<span class="w-status">{}</span>',
    #         _("Draft"),
    #     )
    
    def get_extra_class_names_for_field_col(self, obj, field_name):
        if field_name == '__str__':
            if not obj.live:
                return ['unpublished']
        return []


class CAPAlertWebhookAdmin(ModelAdmin):
    model = CAPAlertWebhook
    menu_label = _('Webhooks')
    menu_icon = 'multi-cluster-sector'


class CAPAlertWebhookEventPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False
    
    def user_can_edit_obj(self, user, obj):
        return False
    
    def user_can_delete_obj(self, user, obj):
        return False
    
    def user_can_copy_obj(self, user, obj):
        return False


class CAPAlertWebhookEventAdmin(ModelAdmin):
    model = CAPAlertWebhookEvent
    menu_label = _('Webhook Events')
    menu_icon = 'notification'
    list_display = ('webhook', 'alert', 'created', 'status',)
    list_filter = ('status', 'webhook',)
    inspect_view_enabled = True
    
    permission_helper_class = CAPAlertWebhookEventPermissionHelper


class CAPAlertMQTTAdmin(ModelAdmin):
    model = CAPAlertMQTTBroker
    menu_label = CAPAlertMQTTBroker._meta.verbose_name_plural
    menu_icon = 'globe'
    list_display = ('name', 'host', 'port', 'created', 'modified')
    list_filter = ('wis2box_metadata_id', 'active')
    search_fields = ('name', 'wis2box_metadata_id')
    
    form_view_extra_js = ['cap/js/mqtt_collapse_panels.js']


class CAPAlertMQTTEventPermissionHelper(PermissionHelper):
    def user_can_create(self, user):
        return False
    
    def user_can_edit_obj(self, user, obj):
        return False
    
    def user_can_delete_obj(self, user, obj):
        return False
    
    def user_can_copy_obj(self, user, obj):
        return False


class CAPAlertMQTTEventAdmin(ModelAdmin):
    model = CAPAlertMQTTBrokerEvent
    menu_label = CAPAlertMQTTBrokerEvent._meta.verbose_name_plural
    menu_icon = 'notification'
    list_display = ('broker', 'alert', 'created', 'status')
    list_filter = ('broker', 'status')
    inspect_view_enabled = True
    
    permission_helper_class = CAPAlertMQTTEventPermissionHelper


class CAPExternalFeedAdmin(ModelAdmin):
    model = ExternalAlertFeed
    menu_label = _('External CAP Alert Feeds')
    menu_icon = 'link'


class CAPMenuGroupAdminMenuItem(GroupMenuItem):
    def is_shown(self, request):
        return request.user.has_perm("cap.can_view_alerts_menu")


class CAPMenuGroup(ModelAdminGroup):
    menu_label = _('AlertWise')
    menu_icon = 'warning'  # change as required
    menu_order = 200  # will put in 3rd place (000 being 1st, 100 2nd)
    items = (
        CAPAdmin,
        CAPAlertWebhookAdmin,
        CAPAlertWebhookEventAdmin,
        CAPAlertMQTTAdmin,
        CAPAlertMQTTEventAdmin,
        CAPExternalFeedAdmin
    )
    
    def get_menu_item(self, order=None):
        if self.modeladmin_instances:
            submenu = Menu(items=self.get_submenu_items())
            return CAPMenuGroupAdminMenuItem(self, self.get_menu_order(), submenu)
    
    def get_submenu_items(self):
        menu_items = []
        item_order = 1
        
        for modeladmin in self.modeladmin_instances:
            menu_items.append(modeladmin.get_menu_item(order=item_order))
            item_order += 1
        
        try:
            
            # add CAP import menu
            settings_url = reverse("load_cap_alert")
            import_cap_menu = MenuItem(label=_("Import CAP Alert"), url=settings_url, icon_name="upload")
            menu_items.append(import_cap_menu)
            
            # add settings menu
            settings_url = reverse(
                "wagtailsettings:edit",
                args=[CapSetting._meta.app_label, CapSetting._meta.model_name, ],
            )
            gm_settings_menu = MenuItem(label=_("CAP Base Settings"), url=settings_url, icon_name="cog")
            menu_items.append(gm_settings_menu)
            
            #  add other cap settings menu
            settings_url = reverse("wagtailsettings:edit",
                                   args=[OtherCAPSettings._meta.app_label,
                                         OtherCAPSettings._meta.model_name, ], )
            
            other_cap_settings_menu = MenuItem(label=_("Other Settings"), url=settings_url,
                                               icon_name="cog")
            
            menu_items.append(other_cap_settings_menu)
        
        except Exception:
            pass
        
        return menu_items


modeladmin_register(CAPMenuGroup)


@hooks.register('construct_settings_menu')
def hide_settings_menu_item(request, menu_items):
    hidden_settings = ["cap-settings", "cap-geomanager-settings", "other-cap-settings"]
    menu_items[:] = [item for item in menu_items if item.name not in hidden_settings]


@hooks.register("before_copy_page")
def copy_cap_alert_page(request, page):
    if page.specific.__class__.__name__ == "CapAlertPage":
        # Parent page defaults to parent of source page
        parent_page = page.get_parent()
        
        # Check if the user has permission to publish subpages on the parent
        can_publish = parent_page.permissions_for_user(request.user).can_publish_subpage()
        
        # Create the form
        form = CopyForm(
            request.POST or None, user=request.user, page=page, can_publish=can_publish
        )
        
        copy_form_fields_to_exclude = [
            "publish_copies",
            "alias",
        ]
        
        for field in copy_form_fields_to_exclude:
            if form.fields.get(field):
                form.fields.pop(field)
        
        alert_page_fields_to_exclude = [
            "alert_area_map_image",
            "alert_pdf_preview",
            "expires",
            "search_image",
            "search_description",
        ]
        
        # Check if user is submitting
        if request.method == "POST":
            # Prefill parent_page in case the form is invalid (as prepopulated value for the form field,
            # because ModelChoiceField seems to not fall back to the user given value)
            parent_page = Page.objects.get(id=request.POST["new_parent_page"])
            
            if form.is_valid():
                # Receive the parent page (this should never be empty)
                if form.cleaned_data["new_parent_page"]:
                    parent_page = form.cleaned_data["new_parent_page"]
                
                action = CopyPageAction(
                    page=page,
                    recursive=form.cleaned_data.get("copy_subpages"),
                    to=parent_page,
                    update_attrs={
                        "title": form.cleaned_data["new_title"],
                        "slug": form.cleaned_data["new_slug"],
                        "sent": timezone.localtime(),
                    },
                    keep_live=False,
                    copy_revisions=False,
                    user=request.user,
                    exclude_fields=alert_page_fields_to_exclude,
                )
                
                new_page = action.execute()
                
                messages.success(
                    request,
                    _("Alert '%(page_title)s' copied. You can edit the new alert below.")
                    % {"page_title": page.specific_deferred.get_admin_display_title()},
                )
                
                for fn in hooks.get_hooks("after_copy_page"):
                    result = fn(request, page, new_page)
                    if hasattr(result, "status_code"):
                        return result
                
                # redirect to the edit copied page
                return redirect(reverse("wagtailadmin_pages:edit", args=(new_page.id,)))
        
        return TemplateResponse(
            request,
            "wagtailadmin/pages/copy.html",
            {
                "page": page,
                "form": form,
            },
        )
    
    return


@hooks.register("before_edit_page")
def before_edit_cap_alert_page(request, page):
    page = page.specific
    if page.__class__.__name__ == "CapAlertPage":
        # allow editing if enabled from settings
        can_edit_cap = getattr(settings, "CAP_ALLOW_EDITING", False)
        if can_edit_cap:
            return
        if page.live and page.status == "Actual":
            url = AdminURLHelper(page).get_action_url("index")
            messages.warning(request, gettext(
                "Actual Alerts cannot be edited after they have been published. To publish an update to this alert, "
                "create a new alert of Message Type 'Update' and reference this alert"))
            return redirect(url)


@hooks.register("before_unpublish_page")
def before_unpublish_cap_alert_page(request, page):
    page = page.specific
    if page.__class__.__name__ == "CapAlertPage":
        if page.live and page.status == "Actual":
            url = AdminURLHelper(page).get_action_url("index")
            messages.warning(request, gettext("Actual Alerts cannot be Unpublished after they have been published"))
            return redirect(url)


@hooks.register("before_delete_page")
def before_delete_cap_alert_page(request, page):
    page = page.specific
    if page.__class__.__name__ == "CapAlertPage":
        if page.live and page.status == "Actual":
            url = AdminURLHelper(page).get_action_url("index")
            messages.warning(request, gettext(
                "Actual Alerts cannot be deleted after they have been published. To cancel or publish an update "
                "to this alert, create a new alert of Message Type 'Cancel' or 'Update' and reference this alert"))
            return redirect(url)


@hooks.register("before_import_cap_alert")
def import_cap_alert(request, alert_data):
    new_cap_alert_page = create_draft_alert_from_alert_data(alert_data, request)
    
    if not new_cap_alert_page:
        return None
    
    messages.success(request, gettext("CAP Alert draft created. You can now edit the alert."))
    return redirect(reverse("wagtailadmin_pages:edit", args=[new_cap_alert_page.id]))


@hooks.register("register_icons")
def register_icons(icons):
    brands = [
        'wagtailfontawesomesvg/brands/facebook.svg',
        'wagtailfontawesomesvg/brands/twitter.svg',
        'wagtailfontawesomesvg/brands/linkedin.svg',
        'wagtailfontawesomesvg/brands/telegram.svg',
        'wagtailfontawesomesvg/brands/whatsapp.svg',
    ]
    
    return icons + [
        'cap/icons/category.svg',
        'cap/icons/certainty.svg',
        'cap/icons/clock.svg',
        'cap/icons/language.svg',
        'cap/icons/response.svg',
        'cap/icons/warning.svg',
        'cap/icons/warning-outline.svg',
        'cap/icons/x-twitter.svg',
    ] + brands


@hooks.register("register_permissions")
def register_permissions():
    return Permission.objects.filter(content_type__app_label="cap")
