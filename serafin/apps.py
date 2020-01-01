from django.apps import AppConfig, apps
from django.contrib import admin
from django.contrib.admin import sites
from django.utils.translation import ugettext_lazy as _
from suit.apps import DjangoSuitConfig
from suit.menu import ParentItem, ChildItem

class SerafinReConfig(AppConfig):
    name = 'serafin'

    def ready(self):
        from request.models import Request
        from .models import CustomRequestAdmin
        apps.get_app_config('auth').verbose_name = _('Permissions')
        apps.get_app_config('filer').verbose_name = _('Filer')

        admin.site.unregister(Request)
        admin.site.register(Request, CustomRequestAdmin)


class SuitConfig(DjangoSuitConfig):
    layout = 'vertical'

    verbose_name = 'Serafin Admin'

    menu = (
        ParentItem('Users', 'users', icon='icon-user', children=[
            ChildItem(model='user'),
            ChildItem(model='auth.group')
        ]),
        ParentItem('Program', 'system', icon='icon-wrench', children=[
            ChildItem(model='program'),
            ChildItem(model='session'),
            ChildItem(model='page'),
            ChildItem(model='email'),
            ChildItem(model='sms'),
            ChildItem(model='variable')
        ]),
        ParentItem('Events', 'events', icon='icon-bullhorn', children=[
            ChildItem(model='event'),
            ChildItem(model='tasker.task'),
            ChildItem(model='request.request')
        ]),
        ParentItem('Media', 'filer', icon='icon-picture'),
        ParentItem('Settings', 'sites', icon='icon-cog', children=[
            ChildItem(model='site'),
            ChildItem(model='sitetree.tree'),
            ChildItem(model='constance.config')
        ])
    )
