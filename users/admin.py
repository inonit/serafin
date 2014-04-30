from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from import_export import resources, fields, widgets
from import_export.admin import ImportExportModelAdmin
from jsonfield import JSONField
from users.models import User


class UserCreationForm(forms.ModelForm):
    '''Custom User creation form'''
    password1 = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Password (again)'), widget=forms.PasswordInput)

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

    def clean_password(self):
        return self.initial['password']

    class Meta:
        model = User


class UserResource(resources.ModelResource):
    '''Import-Export resource for User model'''

    data = fields.Field(column_name='...')
    data_headers = []

    def import_obj(self, obj, data, dry_run):
        fields = [field for field in self.get_fields() if field.column_name != '...']

        for field in fields:
            if isinstance(field.widget, widgets.ManyToManyWidget):
                continue
            self.import_field(field, obj, data)

        headers = [field.column_name for field in self.get_fields() if field.column_name != '...']

        for key in data.keys():
            if key in headers:
                continue
            if not obj.data:
                obj.data = {}
            obj.data[key] = data[key]

    def export_resource(self, obj):
        fields = [self.export_field(field, obj) for field in self.get_fields() if field.column_name != '...']

        for field in self.data_headers:
            if field in obj.data:
                fields.append(obj.data.get(field))

        return fields

    def get_export_headers(self):
        headers = [field.column_name for field in self.get_fields() if field.column_name != '...']
        queryset = self.get_queryset()

        data_headers = set()
        for obj in queryset:
            data_headers.update(obj.data.keys())

        self.data_headers = list(data_headers)
        headers += self.data_headers

        return headers

    class Meta:
        model = User
        export_order = [
            'id',
            'groups',
            'data'
        ]
        exclude = [
            'password',
            'last_login',
            'is_superuser',
            'user_permissions',
            'is_staff',
            'is_active',
            'date_joined',
            'token',
            'data',
        ]


class UserDataWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        context = {
            'value': value,
        }
        html = render_to_string('admin/userdata_widget.html', context)
        return mark_safe(html)

    class Media:
        js = (
            'plumbing/angular/angular.min.js',
        )


class UserAdmin(UserAdmin, ImportExportModelAdmin):
    list_display = ['id', 'date_joined', 'last_login', 'is_superuser', 'is_staff', 'is_active']
    ordering = ['-date_joined']
    date_hierarchy = 'date_joined'

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {'fields': ('id', 'password')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('User data'), {'fields': ('data', )}),
    )
    add_fieldsets = (
        (None, {'fields': ('password1', 'password2')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
    )
    readonly_fields = [
        'id',
        'date_joined',
        'last_login',
    ]
    formfield_overrides = {
        JSONField: { 'widget': UserDataWidget }
    }

    resource_class = UserResource


admin.site.register(User, UserAdmin)
