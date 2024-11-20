from django.db import models
from django.utils.translation import gettext_lazy as _


class CAPMenuPermission(models.Model):
    class Meta:
        verbose_name = _('CAP Menu Permission')
        verbose_name_plural = _('CAP Menu Permissions')
        default_permissions = ([])
        
        permissions = (
            ('can_view_alerts_menu', 'Can view CAP Alerts Menu'),
        )
