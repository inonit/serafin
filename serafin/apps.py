from django.apps import AppConfig, apps
from django.contrib import admin
from django.contrib.admin import sites
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from request.models import Request
from request.admin import RequestAdmin


class SerafinReConfig(AppConfig):
    name = 'serafin'

    def ready(self):
        apps.get_app_config('auth').verbose_name = _('Permissions')
        apps.get_app_config('filer').verbose_name = _('Filer')

        admin.site.unregister(Request)
        admin.site.register(Request, CustomRequestAdmin)


class CustomRequestAdmin(RequestAdmin):
    list_display = ['time', 'method', 'path', 'response', 'ip_filter', 'user_link']
    search_fields = ['path', 'ip', 'user_id']
    date_hierarchy = 'time'

    def has_add_permission(self, request):
        return False

    def user_link(self, obj):
        if obj.user_id:
            user = obj.get_user()
            url = reverse('admin:users_user_change', args=[user.id])
            return '<a href="%s">%s</a>' % (url, user)

    user_link.short_description = _('User')
    user_link.allow_tags = True
    user_link.admin_order_field = 'user_id'

    def ip_filter(self, obj):
        return '<a href="?ip={0}" title="{1}">{0}</a>'.format(
            obj.ip,
            _('Show only requests from this IP address.'),
        )

    ip_filter.short_description = _('IP')
    ip_filter.allow_tags = True
    ip_filter.admin_order_field = 'ip'

