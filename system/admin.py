from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.db import models
from django.contrib import admin
from suit.widgets import SuitSplitDateTimeWidget, LinkedSelect, AutosizedTextarea, NumberInput
from jsonfield import JSONField

from django.contrib.auth.models import Group
from system.models import Program, ProgramGroupAccess, Session, Page, Email, SMS
from plumbing.widgets import PlumbingWidget
from content.widgets import ContentWidget, TextContentWidget, SMSContentWidget


class ProgramGroupAccessInline(admin.TabularInline):
    model = Program.groups.through
    extra = 0
    ordering = ['start_time']

    formfield_overrides = {
        models.ForeignKey: {
            'widget': LinkedSelect
        },
        models.DateTimeField: {
            'widget': SuitSplitDateTimeWidget
        },
        models.DecimalField: {
            'widget': forms.NumberInput(attrs={'class': 'input-mini'})
        },
    }


class ProgramAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_excerpt', 'group_access']
    search_fields = ['title', 'admin_note', 'groups__name']
    actions = ['copy']

    inlines = [ProgramGroupAccessInline]
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
    }

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def group_access(self, obj):
        return ', '.join([group.__unicode__() for group in obj.groups.all()])

    group_access.short_description = _('Group access')

    def copy(modeladmin, request, queryset):
        for program in queryset:
            sessions = list(program.session_set.all())

            program.pk = None
            program.title = _('Copy of %(title)s' % {'title': program.title})
            program.save()

            for session in sessions:
                contents = list(session.content.all())

                session.pk = None
                session.title = _('Copy of %(title)s' % {'title': session.title})
                session.program_id = program.id
                session.save()
                session.content = []

                nodes = session.data.get('nodes')

                for content in contents:
                    orig_id = content.id

                    content.pk = None
                    content.title = _('Copy of %(title)s' % {'title': content.title})
                    content.save()

                    session.content.add(content)

                    for node in nodes:
                        ref_id = node.get('ref_id')
                        if ref_id and int(ref_id) == orig_id:
                            node['ref_id'] = content.id
                            node['title'] = content.title

                session.data['nodes'] = nodes
                session.save()

    copy.short_description = _('Copy selected programs')


class SessionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)
        if 'data' in self.fields:
            self.fields['data'].help_text = ''

    class Meta:
        model = Session
        widgets = {
            'start_time_unit': forms.Select(attrs={'class': 'input-small'}),
            'end_time_unit': forms.Select(attrs={'class': 'input-small'}),
        }


class SessionAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'program',
        'note_excerpt',
        'start_time_delta',
        'start_time_unit',
        'end_time_delta',
        'end_time_unit',
        'start_time'
    ]
    list_editable = ['start_time_delta', 'start_time_unit', 'end_time_delta', 'end_time_unit']
    list_filter = ['program__title']
    search_fields = ['title', 'admin_note', 'program__title']
    ordering = ['start_time']
    date_hierarchy = 'start_time'
    actions = ['copy']

    form = SessionForm
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
        return SessionForm

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def copy(modeladmin, request, queryset):
        for session in queryset:
            contents = list(session.content.all())

            session.pk = None
            session.title = _('Copy of %(title)s' % {'title': session.title})
            session.save()
            session.content = []

            nodes = session.data.get('nodes')

            for content in contents:
                orig_id = content.id

                content.pk = None
                content.title = _('Copy of %(title)s' % {'title': content.title})
                content.save()

                session.content.add(content)

                for node in nodes:
                    ref_id = node.get('ref_id')
                    if ref_id and int(ref_id) == orig_id:
                        node['ref_id'] = content.id
                        node['title'] = content.title

            session.data['nodes'] = nodes
            session.save()

    copy.short_description = _('Copy selected sessions')


class ContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''


class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'admin_note', 'data']
    actions = ['copy']

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
                display = obj.data[0]['content'][:100] + '...'
            else:
                display = '(%s data)' % obj.data[0]['content_type']
        return display

    page_excerpt.short_description = _('Page excerpt')

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def copy(modeladmin, request, queryset):
        for content in queryset:
            content.pk = None
            content.title = _('Copy of %(title)s' % {'title': content.title})
            content.save()

    copy.short_description = _('Copy selected content')


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
            "content": ""
        }]'''


class EmailForm(TextContentForm):
    class Meta:
        model = Email


class EmailAdmin(ContentAdmin):
    form = EmailForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': TextContentWidget
        }
    }


class SMSForm(TextContentForm):
    class Meta:
        model = SMS


class SMSAdmin(ContentAdmin):
    form = SMSForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': SMSContentWidget
        }
    }


admin.site.register(Program, ProgramAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Email, EmailAdmin)
admin.site.register(SMS, SMSAdmin)
