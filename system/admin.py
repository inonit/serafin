from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import models
from django.contrib import admin
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect, AutosizedTextarea, NumberInput
from jsonfield import JSONField

from system.models import Program, Part, Page, Email, SMS
from plumbing.widgets import PlumbingWidget
from content.widgets import ContentWidget, TextContentWidget


class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_excerpt', 'start_time', 'time_factor']
    search_fields = ['title', 'admin_note']
    ordering = ['start_time']
    date_hierarchy = 'start_time'

    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        models.DateTimeField: {
            'widget': SuitSplitDateTimeWidget
        },
        models.DecimalField: {
            'widget': forms.NumberInput(attrs={'class': 'input-mini'})
        },
    }

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')


class PartForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PartForm, self).__init__(*args, **kwargs)
        if 'data' in self.fields:
            self.fields['data'].help_text = ''

    class Meta:
        model = Part
        widgets = {
            'start_time_unit': forms.Select(attrs={'class': 'input-small'}),
            'end_time_unit': forms.Select(attrs={'class': 'input-small'}),
        }


class PartAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'program',
        'note_excerpt',
        'program_start_time',
        'start_time_delta',
        'start_time_unit',
        'end_time_delta',
        'end_time_unit',
        'program_time_factor',
        'start_time',
    ]
    list_editable = ['start_time_delta', 'start_time_unit', 'end_time_delta', 'end_time_unit']
    list_filter = ['program__title']
    search_fields = ['title', 'admin_note', 'program']
    ordering = ['start_time']
    date_hierarchy = 'start_time'

    form = PartForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        models.IntegerField: {
            'widget': NumberInput(attrs={'class': 'input-mini'})
        },
        JSONField: {
            'widget': PlumbingWidget
        },
    }
    fieldsets = [
        (None, {
            'fields': [
                'title',
                'program',
                'admin_note',
                'start_time_delta',
                'start_time_unit',
                'end_time_delta',
                'end_time_unit',
            ]
        }),
        (None, {
            'classes': ('full-width', ),
            'fields': ['data']
        }),
    ]

    def get_changelist_form(self, request, **kwargs):
        return PartForm

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def program_start_time(self, obj):
        return obj.program.start_time

    program_start_time.short_description = _('Program start time')

    def program_time_factor(self, obj):
        return obj.program.time_factor

    program_time_factor.short_description = _('Program time factor')


class ContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''


class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'admin_note', 'data']

    form = ContentForm
    fields = ['title', 'admin_note', 'data']
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': ContentWidget
        }
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


class PageForm(ContentForm):
    class Meta:
        model = Page


class PageAdmin(ContentAdmin):
    form = PageForm


class TextContentForm(ContentForm):
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''
        self.fields['data'].initial = '''[{
            "content_type": "text",
            "content": {
                "text": "",
                "html": ""
            }
        }]'''


class TextContentAdmin(ContentAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': TextContentWidget
        }
    }


class EmailForm(TextContentForm):
    class Meta:
        model = Email


class EmailAdmin(TextContentAdmin):
    form = EmailForm


class SMSForm(TextContentForm):
    class Meta:
        model = SMS


class SMSAdmin(TextContentAdmin):
    form = SMSForm


admin.site.register(Program, ProgramAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(SMS, SMSAdmin)
