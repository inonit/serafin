from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
import requests
import json


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254)

    def save(self, *args, **kwargs):
        '''Ask the vault to send a one-time login link for the given email'''

        current_site = Site.objects.get_current()

        url = '%(server_url)s%(path)s' % {
            'server_url': settings.VAULT_SERVER_API_URL,
            'path': settings.VAULT_PASSWORD_RESET_PATH,
        }

        data = {
            'email': self.cleaned_data['email'],
            'protocol': 'https' if settings.USE_HTTPS else 'http',
            'domain': current_site.domain,
            'path': reverse('password_reset'),
            'site_name': current_site.name,
        }

        headers = {
            'content-type': 'application/json',
        }

        response = requests.post(url, data=json.dumps(data), headers=headers)
        response.raise_for_status()


class AdminIDAuthenticationForm(AdminAuthenticationForm):

    def clean_username(self):
        try:
            username = int(self.cleaned_data.get('username'))
            return username
        except:
            message = _('ID should be an integer value')
            params = {'username': self.username_field.verbose_name}
            raise forms.ValidationError(message, code='invalid', params=params)


admin.site.login_form = AdminIDAuthenticationForm
