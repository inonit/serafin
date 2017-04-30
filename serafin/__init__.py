from django.contrib import admin
from django.contrib.admin import sites

from request.models import Request
from request.plugins import plugins


class CustomAdminSite(admin.AdminSite):

    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        qs = Request.objects.this_month()
        for plugin in plugins.plugins:
            plugin.qs = qs

        extra_context['plugins'] = plugins.plugins

        return super(CustomAdminSite, self).index(request, extra_context)


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site
sites.site = custom_admin_site

