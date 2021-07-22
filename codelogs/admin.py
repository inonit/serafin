# Register your models here.
from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from codelogs.models import CodeLog


class CodeLogAdmin(admin.ModelAdmin):
    list_display = ['sender_link', 'code_link', 'subject_link', 'time', 'log']
    list_display_links = []
    list_per_page = 100
    search_fields = ['subject__id']
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
            return format_html('<a href="{}">{}</a>', url, instance.subject_id)
        else:
            return None
    subject_link.short_description = _('User')
    subject_link.allow_tags = True
    change_list_template = 'admin/events/event/change_list.html'

    def code_link(self, instance):
        if instance.code:
            url = reverse('admin:%s_%s_change' % (
                instance.code._meta.app_label,
                instance.code._meta.model_name
            ), args=[instance.code_id])
            
            return format_html('<a href="{}">{}</a>',url, instance.code.title)
        else:
            return None
    code_link.short_description = _('Code')
    code_link.allow_tags = True


admin.site.register(CodeLog, CodeLogAdmin)
