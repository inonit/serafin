from __future__ import unicode_literals
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
from events.models import Event
from users.importexport import UserResource
from users.models import User

from filer.admin import FolderAdmin
from filer.models import Folder


class UserCreationForm(forms.ModelForm):
    '''Custom User creation form'''
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'), widget=forms.PasswordInput)
    email = forms.EmailField(label=_('E-mail'))
    phone = forms.CharField(label=_('Phone'))

    class Meta:
        model = User

    def clean_password(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_('The passwords are not equal.'))
        return password1

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        user.data['email'] = self.cleaned_data['email']
        user.data['phone'] = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class BlankWidget(forms.Widget):
    '''A widget that will display nothing'''
    def render(self, name, value, attrs):
        return ''


class BlankPasswordField(forms.Field):
    '''Custom blank password field, as admin user does not need to see password algorithm'''
    widget = BlankWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("required", False)
        super(BlankPasswordField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return initial

    def _has_changed(self, initial, data):
        return False


class UserChangeForm(forms.ModelForm):
    '''Custom User change form'''
    password = BlankPasswordField(
        label=_('Password'),
        help_text=_('Password can be changed with <a href="password/">this form</a>.')
    )

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''
        self.fields['is_active'].help_text = _('Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
        self.fields['is_staff'].help_text = _('Designates whether the user can log into this admin site.')

    def clean_password(self):
        return self.initial['password']

    class Meta:
        model = User


class UserDataWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        context = {
            'value': value,
            'debug': unicode(settings.DEBUG).lower()
        }
        html = render_to_string('admin/userdata_widget.html', context)
        return mark_safe(html)

    class Media:
        js = (
            'plumbing/angular/angular.min.js',
        )


class EventInline(admin.TabularInline):
    model = Event
    extra = 0
    can_delete = False
    suit_classes = 'suit-tab suit-tab-log'

    readonly_fields = ('time', 'domain', 'variable', 'pre_value', 'post_value')

    def has_add_permission(self, request):
        return False

    def domain_display(self, instance):
        return instance.get_domain_display()

    domain_display.short_description = _('domain')


class UserAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ['id', 'date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_active']
    search_fields = ['id', 'data']
    ordering = ['id']

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {
            'fields': ('id', 'password', 'last_login', 'date_joined'),
            'classes': ('suit-tab suit-tab-info', ),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'classes': ('suit-tab suit-tab-info', ),
        }),
        (None, {
            'fields': ('data', ),
            'classes': ('suit-tab suit-tab-data', ),
        }),
    )
    add_fieldsets = (
        (None, {
            'fields': ('password1', 'password2', 'email', 'phone'),
            'classes': ('suit-tab suit-tab-info', ),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups'),
            'classes': ('suit-tab suit-tab-info', ),
        }),
    )
    readonly_fields = [
        'id',
        'date_joined',
        'last_login',
    ]
    formfield_overrides = {
        JSONField: { 'widget': UserDataWidget }
    }
    inlines = (EventInline, )
    suit_form_tabs = (
        ('info', _('User info')),
        ('data', _('User data')),
        ('log', _('Log entries'))
    )

    resource_class = UserResource


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
admin.site.register(User, UserAdmin)
admin.site.register(Folder, CustomUserModelFilerAdmin)
