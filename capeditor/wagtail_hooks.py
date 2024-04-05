from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.templatetags.static import static
from django.urls import path
from django.utils.html import format_html
from django.utils.translation import gettext as _
from wagtail import hooks
from wagtail.actions.copy_page import CopyPageAction
from wagtail.admin import messages
from wagtail.admin.forms.pages import CopyForm
from wagtail.admin.utils import get_valid_next_url_from_request
from wagtail.models import Page

from capeditor.views import load_cap_alert, import_cap_alert


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


@hooks.register('register_admin_urls')
def urlconf_stations():
    return [
        path('import-cap/', load_cap_alert, name='load_cap_alert'),
        path('import-cap/import/', import_cap_alert, name='import_cap_alert'),
    ]


# @hooks.register("before_copy_page")
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

        next_url = get_valid_next_url_from_request(request)

        # Remove the publish_copies and alias fields from the form
        form.fields.pop("publish_copies")
        form.fields.pop("alias")

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
                    },
                    keep_live=False,
                    copy_revisions=False,
                    user=request.user,
                )
                new_page = action.execute()

                messages.success(
                    request,
                    _("Page '%(page_title)s' copied.")
                    % {"page_title": page.specific_deferred.get_admin_display_title()},
                )

                for fn in hooks.get_hooks("after_copy_page"):
                    result = fn(request, page, new_page)
                    if hasattr(result, "status_code"):
                        return result

                # Redirect to explore of parent page
                if next_url:
                    return redirect(next_url)
                return redirect("wagtailadmin_explore", parent_page.id)

        return TemplateResponse(
            request,
            "wagtailadmin/pages/copy.html",
            {
                "page": page,
                "form": form,
                "next": next_url,
            },
        )

    return
