from django.apps import AppConfig, apps
from django.contrib import admin
from django.contrib.admin import sites
from django.utils.translation import ugettext_lazy as _


class SerafinReConfig(AppConfig):
    name = 'serafin'

    def ready(self):
        from request.models import Request
        from .models import CustomRequestAdmin
        apps.get_app_config('auth').verbose_name = _('Permissions')
        apps.get_app_config('filer').verbose_name = _('Filer')

        admin.site.unregister(Request)
        admin.site.register(Request, CustomRequestAdmin)
