from __future__ import unicode_literals

import uuid
from builtins import str
from builtins import object
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from import_export.admin import ImportExportModelAdmin
from jsonfield import JSONField
from constance import config
from events.models import Event
from system.models import Program, ProgramUserAccess
from users.importexport import UserResource
from users.models import User

from filer.admin import FolderAdmin
from filer.models import Folder

import json


class UserCreationForm(forms.ModelForm):
    '''Custom User creation form'''
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'), widget=forms.PasswordInput)
    email = forms.EmailField(label=_('E-mail'))
    phone = forms.CharField(label=_('Phone'))
    secondary_phone = forms.CharField(label=_('Secondary Phone'), required=False)
    program_access = forms.ModelChoiceField(label='Program Access', queryset=Program.objects.all())

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)
        if not self.request_user.is_superuser:
            if self.request_user.program_restrictions.exists():
                program_ids = self.request_user.program_restrictions.values_list('id')
                self.fields['program_access'].queryset = Program.objects.filter(id__in=program_ids)
            else:
                self.fields['program_access'].queryset = Program.objects.none()
        else:
            self.fields['program_access'].required = False

    class Meta(object):
        model = User
        exclude = []

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('The passwords are not equal.'))
        return password1

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.secondary_phone = self.cleaned_data['secondary_phone']
        if commit:
            user.save()
        return user


class BlankWidget(forms.Widget):
    '''A widget that will display nothing'''

    def render(self, name, value, attrs=None, renderer=None):
        return ''


class BlankPasswordField(forms.Field):
    '''Custom blank password field, as admin user does not need to see password algorithm'''
    widget = BlankWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super(BlankPasswordField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return initial

    def has_changed(self, initial, data):
        return False


class UserChangeForm(forms.ModelForm):
    '''Custom User change form'''
    password = BlankPasswordField(
        label=_('Password'),
        help_text=_('Password can be changed with <a href="../password/">this form</a>.')
    )

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''
        self.fields['data'].required = False
        self.fields['is_active'].help_text = _(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
        if 'is_staff' in self.fields:
            self.fields['is_staff'].help_text = _('Designates whether the user can log into this admin site.')
        if 'is_therapist' in self.fields:
            self.fields['is_therapist'].help_text = 'Designates whether the user is a therapist.'
        self.fields['secondary_phone'].required = False
        if self.request_user == self.instance:
            self.fields['data'].widget.attrs['allow_clear'] = True

        # get the user's program, add relevant therapist to the list
        user_program = ProgramUserAccess.objects.filter(user=self.instance).first()
        if user_program is not None:
            # find therapist for this program
            self.fields['therapist'].queryset = User.objects.filter(is_therapist=True,
                                                                    program_restrictions=user_program.program)

    def clean_password(self):
        return self.initial['password']

    class Meta(object):
        model = User
        exclude = []


class UserDataWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        priority_fields = [
            field.strip() for field in config.USER_VARIABLE_PROFILE_ORDER.split(',')
            if field
        ]

        other_fields = [
            field for field in list(json.loads(value).keys())
            if field not in priority_fields
        ]

        context = {
            'data': json.loads(value),
            'int_fields': ['session', 'node'],
            'fields': json.dumps(priority_fields + sorted(other_fields)),
            'debug': str(settings.USERDATA_DEBUG).lower(),
            'clear_allowed': str('allow_clear' in self.attrs and self.attrs['allow_clear']).lower()
        }
        html = render_to_string('admin/userdata_widget.html', context)
        return mark_safe(html)

    class Media(object):
        js = (
            'lib/angular/angular.min.js',
        )


@admin.register(User)
class UserAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ['id', 'email', 'phone', 'date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_therapist',
                    'is_active', 'get_first_program']
    search_fields = ['id', 'email', 'phone', 'secondary_phone', 'data']
    ordering = ['id']

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {
            'fields': ('id', 'password', 'email', 'phone', 'secondary_phone', 'last_login', 'date_joined', 'therapist'),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'is_therapist', 'groups', 'program_restrictions'),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (None, {
            'fields': ('data',),
            'classes': ('suit-tab suit-tab-data',),
        }),
    )
    restricted_fieldsets = (
        (None, {
            'fields': ('id', 'password', 'email', 'phone', 'secondary_phone', 'last_login', 'date_joined', 'therapist'),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (_('Permissions'), {
            'fields': ('is_active',),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (None, {
            'fields': ('data',),
            'classes': ('suit-tab suit-tab-data',),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('password1', 'password2', 'email', 'phone', 'secondary_phone'),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'program_restrictions'),
            'classes': ('suit-tab suit-tab-info',),
        }),
    )
    restricted_add_fieldsets = (
        (None, {
            'fields': ('password1', 'password2', 'email', 'phone', 'secondary_phone', 'program_access'),
            'classes': ('suit-tab suit-tab-info',),
        }),
        (_('Permissions'), {
            'fields': ('is_active',),
            'classes': ('suit-tab suit-tab-info',),
        }),
    )
    readonly_fields = [
        'id',
        'date_joined',
        'last_login',
    ]
    filter_horizontal = [
        'groups',
        'program_restrictions'
    ]
    formfield_overrides = {
        JSONField: {'widget': UserDataWidget}
    }
    suit_form_tabs = (
        ('info', _('User info')),
        ('data', _('User data')),
        ('log', _('Log entries'))
    )
    suit_form_includes = (
        ('admin/userlog.html', 'top', 'log'),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request_user = request.user
        return form

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['log'] = Event.objects.filter(actor=object_id).order_by('-time')
        return super(UserAdmin, self).change_view(request, object_id,
                                                  form_url, extra_context=extra_context)

    def get_fieldsets(self, request, obj=None):
        if request.user.is_superuser:
            return super(UserAdmin, self).get_fieldsets(request, obj=obj)
        else:
            if not obj:
                return self.restricted_add_fieldsets
            else:
                return self.restricted_fieldsets

    def get_queryset(self, request):
        queryset = super(UserAdmin, self).get_queryset(request)

        if not request.user.is_superuser:
            if request.user.program_restrictions.exists():
                program_ids = request.user.program_restrictions.values_list('id')
                return queryset.filter(program__id__in=program_ids).filter(is_superuser=False).distinct()
            else:
                return User.objects.none()

        return queryset

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        if 'program_access' in form.cleaned_data:
            program = form.cleaned_data['program_access']
            if program:
                program.enroll(obj)

    def delete_model(self, request, obj):
        # make anonymous email and phone number
        new_email = uuid.uuid4().hex + '@' + uuid.uuid4().hex + '.com'
        obj.email = new_email
        obj.phone = '0'
        obj.secondary_phone = '0'
        obj.save()

    resource_class = UserResource

    class Media(object):
        css = {
            'all': ('//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',)
        }


class CustomUserModelFilerAdmin(FolderAdmin):
    @staticmethod
    def filter_folder(qs, terms=[]):
        for term in terms:
            qs = qs.filter(
                Q(name__icontains=term)
            )
        return qs

    @staticmethod
    def filter_file(qs, terms=[]):
        for term in terms:
            qs = qs.filter(
                Q(name__icontains=term) |
                Q(description__icontains=term) |
                Q(original_filename__icontains=term)
            )
        return qs


admin.site.unregister(Folder)
admin.site.register(Folder, CustomUserModelFilerAdmin)
