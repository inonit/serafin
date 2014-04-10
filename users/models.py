from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template.loader import get_template
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings

from token_auth.tokens import token_generator
from users.decorators import vault_post


class UserManager(BaseUserManager):
    '''Custom User model Manager'''

    def create_user(self, id, password):
        user = self.model()
        user.set_password(password)
        user.save()
        user._mirror_user()
        return user

    def create_superuser(self, id, password):
        user = self.create_user(id=id, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        user._mirror_user()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User, identified by ID and password'''

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, editable=False)

    token = models.CharField(_('token'), max_length=64, blank=True, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'

    @property
    def username(self):
        return _('User %i' % self.id)

    def get_short_name(self):
        return self.username

    def get_full_name(self):
        return self.get_short_name()

    def get_username(self):
        return self.username

    def update_token(self):
        '''Update User authentication token for the Vault'''

        self.token = token_generator.make_token(self.id)
        self.save()

    @vault_post
    def _mirror_user(self):
        '''Get confirmation of or create a corresponding User in the Vault'''
        self.update_token()
        url = settings.VAULT_MIRROR_USER
        return url, self.id, self.token

    @vault_post
    def _delete_mirror(self):
        '''Deletes VaultUser corresponding to User in Vault'''
        self.update_token()
        url = settings.VAULT_DELETE_MIRROR
        return url, self.id, self.token

    @vault_post
    def send_email(self, subject=None, message=None, html_message=None):
        '''Sends an e-mail to the User through the Vault'''
        self.update_token()
        url = settings.VAULT_SEND_EMAIL_URL
        return url, self.id, self.token

    @vault_post
    def send_sms(self, message=None):
        '''Sends an SMS to the User through the Vault'''
        self.update_token()
        url = settings.VAULT_SEND_SMS_URL
        return url, self.id, self.token

    @vault_post
    def fetch_sms(self, message=None):
        '''Sends an SMS to the User through the Vault'''
        self.update_token()
        url = settings.VAULT_SEND_SMS_URL
        return url, self.id, self.token

    def generate_login_link(self):
        '''Generates a login link url'''
        self.update_token()
        current_site = Site.objects.get_current()

        url = '%(protocol)s://%(domain)s%(link)s'
        params = {
            'link': reverse(
                'login_via_email',
                kwargs={
                    'user_id': self.id,
                    'token': self.token,
                }
            ),
            'protocol': 'https' if settings.USE_HTTPS else 'http',
            'domain': current_site.domain
        }
        link = url % params

        return link

    def send_login_link(self):
        ''' Sends user login link via email templates '''

        subject = _("Today's login link")

        html_template = get_template('users/emails/html/login_link.html')
        text_template = get_template('users/emails/text/login_link.html')

        context = {
            'link': self.generate_login_link(),
        }

        text_content = text_template.render(context)
        html_content = html_template.render(context)

        self.send_email(subject, text_content, html_content)

    def __unicode__(self):
        return unicode(self.username)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
