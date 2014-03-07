from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin

from tasks.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['sender', 'action', 'time']
    search_fields = ['sender', 'action']
    ordering = ['time']
    date_hierarchy = 'time'

    fieldsets = [(None, {'fields': ()})]

    def has_add_permission(self, request):
        return False


admin.site.register(Task, TaskAdmin)

