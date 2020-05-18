# this somehow runs before wsgi.py so...

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'serafin.settings')

from django.contrib import admin
from django.contrib.admin import sites


import backports.csv as csv

class CustomAdminSite(admin.AdminSite):

    index_template = 'admin/index.html'

    def index(self, request, extra_context=None):
        from request.models import Request
        from request.plugins import plugins
        from system.models import Program

        if extra_context is None:
            extra_context = {}

        active_program = None
        if request.user.program_restrictions.exists():
            active_program = request.user.program_restrictions.first()
        elif request.user.is_superuser:
            active_program = Program.objects.first()

        if active_program is not None:
            request.session["_program_id"] = active_program.id
        else:
            request.session["_program_id"] = 0

        qs = Request.objects.this_month()
        for plugin in plugins.plugins:
            plugin.qs = qs

        extra_context['plugins'] = plugins.plugins

        return super(CustomAdminSite, self).index(request, extra_context)


custom_admin_site = CustomAdminSite()
admin.site = custom_admin_site
sites.site = custom_admin_site

