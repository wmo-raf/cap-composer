from adminboundarymanager.wagtail_hooks import AdminBoundaryManagerAdminGroup
from wagtail_modeladmin.options import (
    modeladmin_register
)

modeladmin_register(AdminBoundaryManagerAdminGroup)
