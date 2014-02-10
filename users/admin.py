from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib import admin
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
        help_text='Password can be changed with <a href="password/">this form</a>.'
    )

    def clean_password(self):
        return self.initial['password']

    class Meta:
        model = User



class UserAdmin(admin.ModelAdmin):
    model = User
    form = UserChangeForm
    add_form = UserCreationForm
    fields = [
        'id',
        'password',
        'date_joined',
        'last_login',
        'groups',
        'user_permissions',
        'is_superuser',
        'is_staff',
        'is_active',
    ]
    readonly_fields = [
        'id',
        'date_joined',
        'last_login',
    ]


admin.site.register(User, UserAdmin)
