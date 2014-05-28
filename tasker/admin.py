from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.core.urlresolvers import reverse

from tasker.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['sender_link', 'action', 'time', 'task_result']
    list_display_links = []
    search_fields = ['action']
    ordering = ['time']
    date_hierarchy = 'time'

    fieldsets = [(None, {'fields': ()})]

    def has_add_permission(self, request):
        return False

    def sender_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance.content_type.app_label,
            instance.content_type.model
        ), args=[instance.object_id])
        return '<a href="%s">%s</a>' % (url, instance.sender)
    sender_link.short_description = _('Actor')
    sender_link.allow_tags = True

    def task_result(self, obj):
        return obj.task
    task_result.short_description = _('Task result')


admin.site.register(Task, TaskAdmin)

