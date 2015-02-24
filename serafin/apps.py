from django.apps import AppConfig, apps
from django.utils.translation import ugettext_lazy as _


class AppRenameConfig(AppConfig):
    name = 'serafin'

    def ready(self):
        apps.get_app_config('auth').verbose_name = _('Permissions')
        apps.get_app_config('filer').verbose_name = _('Filer')
