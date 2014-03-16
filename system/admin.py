from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.db import models
from django.contrib import admin

from .models import Program, Part, Page
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect, AutosizedTextarea
from jsonfield import JSONField
from plumbing.widgets import PlumbingWidget
from content.widgets import ContentWidget


class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_excerpt',]
    search_fields = ['title', 'admin_note']

    formfield_overrides = {
        models.TextField: { 'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}) }
    }

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'
    note_excerpt.short_description = _('Admin note excerpt')


class PartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PartForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''

    class Meta:
        model = Part


class PartAdmin(admin.ModelAdmin):
    list_display = ['title', 'program', 'note_excerpt', 'start_time', 'end_time']
    list_editable = ['start_time', 'end_time']
    list_filter = ['program__title']
    search_fields = ['title', 'admin_note', 'program']
    ordering = ['start_time']
    date_hierarchy = 'start_time'

    form = PartForm
    formfield_overrides = {
        models.TextField: { 'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}) },
        models.DateTimeField: { 'widget': SuitSplitDateTimeWidget },
        JSONField: { 'widget': PlumbingWidget }
    }

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'
    note_excerpt.short_description = _('Admin note excerpt')


class PageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''

    class Meta:
        model = Page


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'part', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'part', 'admin_note', 'data']

    fields = ['title', 'part', 'admin_note', 'data']
    readonly_fields = ['part']
    form = PageForm
    formfield_overrides = {
        models.TextField: { 'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}) },
        models.ForeignKey: { 'widget': LinkedSelect },
        JSONField: { 'widget': ContentWidget }
    }

    def page_excerpt(self, obj):
        display = _('No content')
        if len(obj.data) > 0:
            if obj.data[0]['content_type'] == 'text':
                display = obj.data[0]['content']['text'][:100] + '...'
            else:
                display = '(%s data)' % obj.data[0]['content_type']
        return display
    page_excerpt.short_description = _('Page excerpt')

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'
    note_excerpt.short_description = _('Admin note excerpt')


admin.site.register(Program, ProgramAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Page, PageAdmin)
