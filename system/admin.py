from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.db import models
from django.contrib import admin

from .models import Program, Part, Page
from plumbing.forms import PlumbingField
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect
from suit.admin import SortableTabularInline

from fluent_contents.admin import PlaceholderFieldAdmin


class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['program']


class PartForm(forms.ModelForm):
    plumbing = PlumbingField()

    class Meta:
        model = Part


class PartAdmin(admin.ModelAdmin):
    list_display = ['title', 'program', 'start_time', 'end_time']
    list_editable = ['start_time', 'end_time']
    list_filter = ['program__title']
    search_fields = ['title', 'program']
    ordering = ['start_time']
    date_hierarchy = 'start_time'

    form = PartForm
    formfield_overrides = {
        models.DateTimeField: { 'widget': SuitSplitDateTimeWidget }
    }


class PageAdmin(PlaceholderFieldAdmin):
    list_display = ['title', 'page_exerpt']
    search_fields = ['title', 'content__contentitems__text__content']

    def page_exerpt(self, obj):
        return ', '.join(
            [item.__unicode__() for item in obj.content.get_content_items()[:5]]
        )
    page_exerpt.short_description = _('Page excerpt')


admin.site.register(Program, ProgramAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Page, PageAdmin)
