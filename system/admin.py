from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.db import models
from django.contrib import admin

from .models import Program, Part, Page
from plumbing.forms import PlumbingField
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect
from suit.admin import SortableTabularInline
from jsonfield import JSONField
from content.widgets import ContentWidget
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField


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


class PageForm(forms.ModelForm):
    dummy_image = FilerImageField()
    dummy_file = FilerFileField()

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''

    class Meta:
        model = Page


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'page_excerpt']
    search_fields = ['title', 'part', 'data']

    fields = ['title', 'part', 'data']
    readonly_fields = ['part']
    form = PageForm

    def page_excerpt(self, obj):
        display = _('No content')
        if len(obj.data) > 0:
            if obj.data[0]['content_type'] == 'text':
                display = obj.data[0]['content'][:100] + '...'
            else:
                display = '(%s data)' % obj.data[0]['content_type']
        return display
    page_excerpt.short_description = _('Page excerpt')

    formfield_overrides = {
        models.ForeignKey: { 'widget': LinkedSelect },
        JSONField: { 'widget': ContentWidget }
    }


admin.site.register(Program, ProgramAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Page, PageAdmin)
