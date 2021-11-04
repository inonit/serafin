from __future__ import unicode_literals

from defender import utils
from django.contrib.auth.forms import SetPasswordForm
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.forms import AdminAuthenticationForm
from django.contrib.sites.models import Site
from django.urls import reverse
from django.template import Context
from django.template.loader import get_template
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from tokens.tokens import token_generator
from django.contrib.auth import get_user_model


class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=_('Email'), max_length=254)

    def save(self, *args, **kwargs):
        '''Send a one-time login link for the given email'''

        User = get_user_model()

        try:
            user = User.objects.get(email__iexact=self.cleaned_data['email'])
        except:
            return

        current_site = Site.objects.get_current()
        protocol = 'https' if settings.USE_HTTPS else 'http'
        domain = current_site.domain
        path = reverse('password_reset')
        site_name = current_site.name

        if user and protocol and domain and path and site_name:

            link = '%(protocol)s://%(domain)s%(path)s%(uid)s/%(token)s' % {
                'protocol': protocol,
                'domain': domain,
                'path': path,
                'uid': urlsafe_base64_encode(force_bytes(user.id)),
                'token': token_generator.make_token(user.id),
            }

            subject_template = get_template('registration/password_reset_subject.txt')
            content_template = get_template('registration/password_reset_email.html')

            context = {
                'site_name': site_name,
                'link': link,
                'user': user,
            }

            subject = subject_template.render({'site_name': site_name})
            subject = ''.join(subject.splitlines())
            content = content_template.render(context)

            if subject and content:
                user.send_email(subject, html_message=content)


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        utils.reset_failed_attempts(username=self.user.username)
        if commit:
            self.user.save()
        return self.user


class AdminIDAuthenticationForm(AdminAuthenticationForm):

    def clean_username(self):
        try:
            username = (self.cleaned_data.get('username')).strip()
            return username
        except:
            message = _('ID should be an integer value')
            params = {'username': self.username_field.verbose_name}
            raise forms.ValidationError(message, code='invalid', params=params)


admin.site.login_form = AdminIDAuthenticationForm
