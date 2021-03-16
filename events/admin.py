from __future__ import unicode_literals

import re

from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.urls import reverse
from import_export.admin import ImportExportModelAdmin
from django.utils.html import format_html

from events.importexport import EventResource
from events.models import Event


class EventAdmin(ImportExportModelAdmin):
    list_display = ['actor_link', 'time', 'domain', 'variable', 'pre_value', 'post_value']
    list_display_links = []
    list_filter = ['time', 'domain']
    list_per_page = 100
    search_fields = ['actor__id', 'domain', 'variable', 'pre_value', 'post_value']
    ordering = ['-time']
    date_hierarchy = 'time'

    def actor_link(self, instance):
        url = reverse('admin:users_user_change', args=[instance.actor.id])
        return format_html('<a href="{}">{} ({})</a>', url, instance.actor.email, instance.actor) #.actor_link())
    actor_link.short_description = _('Actor')
    actor_link.allow_tags = True

    fieldsets = [(None, {'fields': ()})]

    actions = None

    def __init__(self, *args, **kwargs):
        super(EventAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return re.search("user.*delete", request.path)

    resource_class = EventResource
    change_list_template = 'admin/events/event/change_list.html'

    def get_queryset(self, request):
        queryset = super(EventAdmin, self).get_queryset(request)

        if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            return queryset.filter(actor__program__id__in=program_ids).distinct()

        return queryset

admin.site.register(Event, EventAdmin)
