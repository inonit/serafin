from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin

from .models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['sender', 'action', 'time', 'task_result']
    search_fields = ['sender', 'action', 'task_result']
    ordering = ['time']
    date_hierarchy = 'time'

    fieldsets = [(None, {'fields': ()})]

    def has_add_permission(self, request):
        return False

    def task_result(self, obj):
        return obj.get_result()
    task_result.short_description = _('Task result')


admin.site.register(Task, TaskAdmin)

