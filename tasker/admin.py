from __future__ import unicode_literals

from django.utils.html import format_html
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.urls import reverse

from tasker.models import Task


class TaskAdmin(admin.ModelAdmin):
    list_display = ['sender_link', 'action', 'subject_link', 'time', 'task_result']
    list_display_links = []
    list_per_page = 100
    search_fields = ['subject__id', 'domain', 'action']
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
        return format_html('<a href="{}">{}</a>', url, instance.sender)
    sender_link.short_description = _('Source')
    sender_link.allow_tags = True

    def subject_link(self, instance):
        if instance.subject:
            url = reverse('admin:%s_%s_change' % (
                instance.subject._meta.app_label,
                instance.subject._meta.model_name
            ), args=[instance.subject_id])
            return format_html('<a href="{}">{}</a>', url, instance.subject)
        else:
            return None
    subject_link.short_description = _('User')
    subject_link.allow_tags = True

    def task_result(self, obj):
        try:
            res = obj.result
        except Exception as ex:
            res = "Error: %s" % ex
        return res
    task_result.short_description = _('Task result')

    def get_queryset(self, request):
        queryset = super(TaskAdmin, self).get_queryset(request)

        if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            return queryset.filter(subject__program__id__in=program_ids)

        return queryset


admin.site.register(Task, TaskAdmin)

