from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib import admin
from django.core.urlresolvers import reverse

from events.models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = ['actor_link', 'time', 'domain', 'variable', 'pre_value', 'post_value']
    list_display_links = []
    list_filter = ['time', 'domain']
    search_fields = ['domain', 'variable', 'pre_value', 'post_value']
    ordering = ['-time']
    date_hierarchy = 'time'

    def actor_link(self, instance):
        url = reverse('admin:users_user_change', args=[instance.actor.id])
        return '<a href="%s">%s</a>' % (url, instance.actor.actor_link())
    actor_link.short_description = _('Actor')
    actor_link.allow_tags = True

    fieldsets = [(None, {'fields': ()})]

    actions = None

    def __init__(self, *args, **kwargs):
        super(EventAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = (None, )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Event, EventAdmin)
