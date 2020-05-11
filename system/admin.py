from __future__ import unicode_literals

from builtins import str
from builtins import object
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import models, IntegrityError
from django.db.models import Q
from django.http import HttpResponseRedirect
from adminsortable.admin import NonSortableParentAdmin, SortableStackedInline

from suit.widgets import AutosizedTextarea
from jsonfield import JSONField
from reversion.admin import VersionAdmin

from system.models import Variable, Program, Session, Content, Page, Email, SMS, Chapter, Module
from system.expressions import Parser
from plumbing.widgets import PlumbingWidget
from content.widgets import ContentWidget, TextContentWidget, SMSContentWidget


class VariableForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VariableForm, self).__init__(*args, **kwargs)
        self.fields['value'].help_text = _('Initial value remains static unless '
            'set as a user value using a hidden set value field.')
        self.fields['user_editable'].help_text = _('User editable fields can be changed '
            'at any time by the user on their profile page.')
        self.fields['random_type'].help_text = _('Setting a randomization type will '
            'set the variable to a random value.')
        self.fields['randomize_once'].help_text = _('If set, this value will be randomized '
            'once for each user when the Variable is first saved OR changed, then once for '
            'each new user.')
        self.fields['random_set'].help_text = _('The value of the Variable will be randomly '
            'selected from a set of comma separated strings in this field.')
        self.fields['is_array'].help_text = 'The variable accumulate data as array'

    def clean_name(self):
        data = self.cleaned_data['name']
        if data in [var['name'] for var in settings.RESERVED_VARIABLES]:
            raise forms.ValidationError(_('You are trying to use a reserved variable name'))
        return data

    class Meta(object):
        model = Variable
        exclude = []
        widgets = {
            'admin_note': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'}),
            'range_min': forms.NumberInput(attrs={'class': 'input-mini'}),
            'range_max': forms.NumberInput(attrs={'class': 'input-mini'}),
            'random_set': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        }


@admin.register(Variable)
class VariableAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'value', 'random_type', 'user_editable']
    search_fields = ['name']
    form = VariableForm

    fieldsets = (
        (None, {
            'fields': (
                'name',
                'display_name',
                'admin_note',
                'program',
                'value',
                'user_editable',
                'random_type',
                'randomize_once',
                'range_min',
                'range_max',
                'random_set',
                'is_array',
            ),
            'classes': ('suit-tab suit-tab-variable', ),
        }),
    )
    suit_form_tabs = (
        ('variable', _('Variable')),
        #('values', _('User values')),
    )

    class Media(object):
        js = ['admin/variable.js']

    def get_queryset(self, request):
        queryset = super(VariableAdmin, self).get_queryset(request)

        if '_program_id' in request.session:
            queryset = queryset.filter(program__id=request.session['_program_id'])

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids)
            else:
                return Variable.objects.none()

        return queryset

    def get_form(self, request, obj=None, **kwargs):
         form = super(VariableAdmin, self).get_form(request, obj, **kwargs)
         if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            form.base_fields['program'].queryset = Program.objects.filter(id__in=program_ids)
         return form

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_variable', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_variable', obj)


class ProgramUserAccessInline(admin.TabularInline):
    model = Program.users.through
    extra = 0
    ordering = ['user_id']

    formfield_overrides = {
        models.ForeignKey: {
            'widget': forms.Select
        },
        models.DecimalField: {
            'widget': forms.NumberInput(attrs={'class': 'input-mini'})
        },
    }


class ProgramGoldVariableInline(admin.TabularInline):
    model = Program.gold_variables.through
    extra = 0
    ordering = ['variable_id']

    formfield_overrides = {
        models.ForeignKey: {
            'widget': forms.Select
        }
    }


@admin.register(Program)
class ProgramAdmin(VersionAdmin):
    list_display = ['title', 'display_title', 'note_excerpt']
    search_fields = ['title', 'display_title', 'admin_note']
    actions = ['copy', 'export_text', 'import_text']
    save_as = True

    inlines = [ProgramUserAccessInline, ProgramGoldVariableInline]
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
    }

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def copy(modeladmin, request, queryset):
        # keep track of copied content to avoid more than one copy
        copied_content = {}

        for program in queryset:
            sessions = list(program.session_set.all())

            program.users.clear()
            program.pk = None
            while not program.pk:
                try:
                    program.title = _('%(title)s (copy)') % {'title': program.title}
                    program.save()
                except IntegrityError:
                    pass

            for session in sessions:

                session.program_id = program.id

                if session.route_slug:
                    try:
                        slug, counter = session.route_slug.rsplit('-', 1)
                    except ValueError:
                        slug, counter = session.route_slug, None
                    if counter and counter.isdigit():
                        counter = int(counter)
                        counter += 1
                        slug = '-'.join([slug, str(counter)])
                    elif counter:
                        slug = '-'.join([slug, str(counter), '1'])
                    else:
                        slug = '-'.join([slug, '1'])

                    session.route_slug = slug

                session.pk = None
                while not session.pk:
                    try:
                        session.title = _('%(title)s (copy)') % {'title': session.title}
                        session.save()
                    except IntegrityError:
                        pass

                nodes = session.data.get('nodes')
                ids = [
                    node['ref_id'] for node in nodes
                    if node['type'] in ['page', 'email', 'sms']
                ]
                contents = Content.objects.filter(id__in=ids)

                for content in contents:
                    orig_id = content.id

                    if orig_id in copied_content:
                        content = copied_content[orig_id]
                    else:
                        content.pk = None
                        while not content.pk:
                            try:
                                content.title = _('%(title)s (copy)') % {'title': content.title}
                                content.save()
                                copied_content[orig_id] = content
                            except IntegrityError:
                                pass

                    for node in nodes:
                        ref_id = node.get('ref_id')
                        if ref_id and int(ref_id) == orig_id:
                            node['ref_id'] = content.id
                            node['title'] = content.title

                session.data['nodes'] = nodes
                session.save()

    copy.short_description = _('Copy selected programs')

    def export_text(modeladmin, request, queryset):
        selected = request.POST.getlist(admin.ACTION_CHECKBOX_NAME)
        ct = ContentType.objects.get_for_model(queryset.model)
        return HttpResponseRedirect('/admin/export_text/?ct=%s&ids=%s' % (ct.pk, ','.join(selected)))

    export_text.short_description = _('Export text of selected program')

    def import_text(modeladmin, request, queryset):

        return HttpResponseRedirect('/admin/import_text/?next=%s' % request.path)

    import_text.short_description = _('Import program text')

    def get_queryset(self, request):
        queryset = super(ProgramAdmin, self).get_queryset(request)

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(id__in=program_ids)
            else:
                return Program.objects.none()

        return queryset

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_program', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_program', obj)


class SessionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SessionForm, self).__init__(*args, **kwargs)
        if 'data' in self.fields:
            self.fields['data'].help_text = ''
        if 'route_slug' in self.fields:
            self.fields['route_slug'].help_text = _('URL at which this Session will be available to registered Program users at all times')
            self.fields['route_slug'].required = False
        if 'is_open' in self.fields:
            self.fields['is_open'].help_text = _('Session open even to unregistered users')
        if 'start_time_delta' in self.fields:
            self.fields['start_time_delta'].help_text = _("Relative to the user's start time for the Program")
        if 'scheduled' in self.fields:
            self.fields['scheduled'].help_text = _('Activate automatically for Program users at the given start time')
        if 'trigger_login' in self.fields:
            self.fields['trigger_login'].help_text = _('Trigger a login e-mail at the scheduled time')

    def clean_route_slug(self):
        return self.cleaned_data['route_slug'] or None

    def clean_data(self):
        data = self.cleaned_data['data']
        id = None
        try:
            parser = Parser(user_obj=self.request_user)

            edges = data.get('edges', [])
            for edge in edges:
                id = _('edge %(id)s') % {'id': edge.get('id')}
                expression = edge.get('expression')
                if expression:
                    result = parser.parse(expression)

            nodes = data.get('nodes', [])
            for node in nodes:
                id = _('expression node')
                expression = node.get('expression')
                if node.get('type') == 'expression':
                    result = parser.parse(expression)

        except Exception as e:
            raise forms.ValidationError(_('Error in expression, %(id)s: %(error)s') % {
                    'id': id,
                    'error': e,
                }
            )

        return data

    class Meta(object):
        model = Session
        exclude = []
        widgets = {
            'start_time_unit': forms.Select(attrs={'class': 'input-small'}),
            #'end_time_unit': forms.Select(attrs={'class': 'input-small'}),
        }


@admin.register(Session)
class SessionAdmin(VersionAdmin):
    list_display = [
        'title',
        #'display_title',
        'route_slug',
        'is_open',
        'program',
        'note_excerpt',
        'start_time_delta',
        'start_time_unit',
        #'end_time_delta',
        #'end_time_unit',
        'start_time',
        'scheduled',
        'trigger_login',
    ]
    list_editable = [
        'start_time_delta',
        'start_time_unit',
        #'end_time_delta',
        #'end_time_unit',
        'scheduled',
        'trigger_login',
    ]
    list_filter = ['program__title', 'scheduled', 'trigger_login']
    list_display_links = ['title']
    search_fields = ['title', 'display_title', 'admin_note', 'program__title', 'data']
    ordering = ['start_time']
    date_hierarchy = 'start_time'
    actions = ['copy']
    readonly_fields = ['id']
    save_as = True

    form = SessionForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        models.IntegerField: {
            'widget': forms.NumberInput(attrs={'class': 'input-mini'})
        },
        JSONField: {
            'widget': PlumbingWidget
        },
    }
    fieldsets = [
        (None, {
            'fields': [
                'title',
                #'display_title',
                'route_slug',
                'is_open',
                'program',
                'admin_note',
                'start_time_delta',
                'start_time_unit',
                #'end_time_delta',
                #'end_time_unit',
                'scheduled',
                'trigger_login',
            ]
        }),
        (None, {
            'classes': ('full-width', ),
            'fields': ['data']
        }),
    ]

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')

    def get_queryset(self, request):
        queryset = super(SessionAdmin, self).get_queryset(request)

        if '_program_id' in request.session:
            queryset = queryset.filter(program__id=request.session['_program_id'])

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids)
            else:
                return Session.objects.none()

        return queryset

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_session', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_session', obj)

    def get_form(self, request, obj=None, **kwargs):
         form = super(SessionAdmin, self).get_form(request, obj, **kwargs)
         form.request_user = request.user
         if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            form.base_fields['program'].queryset = Program.objects.filter(id__in=program_ids)
         return form

    def get_changelist_form(self, request, **kwargs):
        return SessionForm

    def copy(modeladmin, request, queryset):
        # keep track of copied content to avoid more than one copy
        copied_content = {}

        for session in queryset:
            if session.route_slug:
                try:
                    slug, counter = session.route_slug.rsplit('-', 1)
                except ValueError:
                    slug, counter = session.route_slug, None

                if counter and counter.isdigit():
                    counter = int(counter)
                    counter += 1
                    slug = '-'.join([slug, str(counter)])
                elif counter:
                    slug = '-'.join([slug, counter, '1'])
                else:
                    slug = '-'.join([slug, '1'])

                session.route_slug = slug

            session.pk = None
            while not session.pk:
                try:
                    session.title = _('%(title)s (copy)') % {'title': session.title}
                    session.save()
                except IntegrityError:
                    pass

            nodes = session.data.get('nodes')
            ids = [
                node['ref_id'] for node in nodes
                if node['type'] in ['page', 'email', 'sms']
            ]
            contents = Content.objects.filter(id__in=ids)

            for content in contents:
                orig_id = content.id

                if orig_id in copied_content:
                    content = copied_content[orig_id]
                else:
                    content.pk = None
                    while not content.pk:
                        try:
                            content.title = _('%(title)s (copy)') % {'title': content.title}
                            content.save()
                            copied_content[orig_id] = content
                        except IntegrityError:
                            pass

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

    def clean_data(self):
        data = self.cleaned_data['data']
        id = None
        try:
            parser = Parser(user_obj=self.request_user)

            for index, pagelet in enumerate(data):

                id = _('pagelet %(id)s') % {'id': index}

                if pagelet.get('content_type') == 'expression':
                    expression = pagelet.get('content', {}).get('value')
                    result = parser.parse(expression)

                if pagelet.get('content_type') == 'conditionalset':
                    for condition in pagelet.get('content', []):
                        expression = condition.get('expression')
                        if expression:
                            result = parser.parse(expression)

        except Exception as e:
            raise forms.ValidationError(_('Error in expression, %(id)s: %(error)s') % {
                    'id': id,
                    'error': e,
                }
            )

        return data


@admin.register(Content)
class ContentAdmin(VersionAdmin):
    list_display = ['title', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'admin_note', 'data']
    actions = ['copy']
    save_as = True

    form = ContentForm
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
            while not content.pk:
                try:
                    content.title = _('%(title)s (copy)') % {'title': content.title}
                    content.save()
                except IntegrityError:
                    pass

    copy.short_description = _('Copy selected content')

    def get_queryset(self, request):
        queryset = super(ContentAdmin, self).get_queryset(request)

        if '_program_id' in request.session:
            queryset = queryset.filter(
                Q(program_id=request.session['_program_id']) |
                Q(program_id=None)
            )

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids)
            else:
                return self.model._default_manager.none()

        return queryset

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_content', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_content', obj)

    def get_form(self, request, obj=None, **kwargs):
         form = super(ContentAdmin, self).get_form(request, obj, **kwargs)
         form.request_user = request.user
         if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            form.base_fields['program'].queryset = Program.objects.filter(id__in=program_ids)
         return form


class PageForm(ContentForm):
    class Meta(object):
        model = Page
        exclude = []


@admin.register(Page)
class PageAdmin(ContentAdmin):
    list_display = ['title', 'display_title', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'display_title', 'admin_note', 'data']
    fields = ['title', 'display_title', 'program', 'admin_note', 'data', 'chapter']
    raw_id_fields = ('chapter',)
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
    def __init__(self, *args, **kwargs):
        super(EmailForm, self).__init__(*args, **kwargs)
        self.fields['display_title'].label = _('Subject')

    class Meta(object):
        model = Email
        exclude = []


@admin.register(Email)
class EmailAdmin(ContentAdmin):
    list_display = ['title', 'subject', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'display_title', 'admin_note', 'data']
    fields = ['title', 'display_title', 'program', 'admin_note', 'data']
    form = EmailForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': TextContentWidget
        }
    }

    def subject(self, obj):
        return obj.display_title

    subject.short_description = _('Subject')


class SMSForm(TextContentForm):
    class Meta(object):
        model = SMS
        exclude = []


@admin.register(SMS)
class SMSAdmin(ContentAdmin):
    fields = ['title', 'admin_note', 'program', 'data']
    form = SMSForm
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})
        },
        JSONField: {
            'widget': SMSContentWidget
        }
    }


@admin.register(Chapter)
class ChapterAdmin(VersionAdmin):
    list_display = ['title', 'display_title', 'module', 'program']
    search_fields = ['title', 'display_title', 'module']
    raw_id_fields = ('module',)

    class Media(object):
        css = {
            'all': ('//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',)
        }

    def get_form(self, request, obj=None, **kwargs):
         form = super(ChapterAdmin, self).get_form(request, obj, **kwargs)
         form.request_user = request.user
         if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            form.base_fields['program'].queryset = Program.objects.filter(id__in=program_ids)
         return form

    def get_queryset(self, request):
        queryset = super(ChapterAdmin, self).get_queryset(request)

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids)
            else:
                return Chapter.objects.none()

        return queryset

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_chapter', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_chapter', obj)


class ChapterInline(SortableStackedInline):
    model = Chapter
    extra = 1


@admin.register(Module)
class ModuleAdmin(NonSortableParentAdmin):
    list_display = ['title', 'display_title', 'program']
    search_fields = ['title', 'display_title']
    inlines = [ChapterInline]

    class Media(object):
        css = {
            'all': ('//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',)
        }

    def get_form(self, request, obj=None, **kwargs):
         form = super(ModuleAdmin, self).get_form(request, obj, **kwargs)
         form.request_user = request.user
         if request.user.program_restrictions.exists():
            program_ids = request.user.program_restrictions.values_list('id')
            form.base_fields['program'].queryset = Program.objects.filter(id__in=program_ids)
         return form

    def get_queryset(self, request):
        queryset = super(ModuleAdmin, self).get_queryset(request)

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids)
            else:
                return Module.objects.none()

        return queryset

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('system.change_module', obj)

    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('system.view_module', obj)
