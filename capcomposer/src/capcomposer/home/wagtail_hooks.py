from adminboundarymanager.wagtail_hooks import AdminBoundaryViewSetGroup
from wagtail import hooks


@hooks.register("register_admin_viewset")
def register_admin_boundary_viewset():
    return AdminBoundaryViewSetGroup()
