from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.core.urlresolvers import reverse

from tasker.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['sender_link', 'action', 'subject_link', 'time', 'task_result']
    list_display_links = []
    search_fields = ['action', 'subject__id']
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
    sender_link.short_description = _('Source')
    sender_link.allow_tags = True

    def subject_link(self, instance):
        if instance.subject:
            url = reverse('admin:%s_%s_change' % (
                instance.subject._meta.app_label,
                instance.subject._meta.model_name
            ), args=[instance.subject_id])
            return '<a href="%s">%s</a>' % (url, instance.subject)
        else:
            return None
    subject_link.short_description = _('User')
    subject_link.allow_tags = True

    def task_result(self, obj):
        return obj.task
    task_result.short_description = _('Task result')


admin.site.register(Task, TaskAdmin)

