from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, AnonymousUser
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.template import Context
from django.template.loader import get_template

from collections import OrderedDict
from jsonfield import JSONField
from plivo import RestAPI as PlivoRestClient
from tokens.tokens import token_generator
from twilio.rest import TwilioRestClient
import requests


class UserManager(BaseUserManager):
    '''Custom User model Manager'''

    def create_user(self, id, password, email, phone, data=None):
        user = self.model()
        user.set_password(password)
        user.email = email
        user.phone = phone
        if data:
            user.data = data
        user.save()
        return user

    def create_superuser(self, id, password, email, phone):
        user = self.create_user(id=id, password=password, email=email, phone=phone)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User, identified by ID and password'''

    email = models.EmailField(_('e-mail address'), max_length=254, unique=True)
    phone = models.CharField(_('phone number'), max_length=32, unique=True)

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, editable=False)

    token = models.CharField(_('token'), max_length=64, blank=True, editable=False)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default={})

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

    def is_member(self, group_name):
        '''Check if user is part of a given group by name'''
        return self.groups.filter(name=group_name).exists()

    def send_sms(self, message=None):
        if message and settings.SMS_SERVICE == 'Twilio':
            client = TwilioRestClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            response = client.messages.create(
                body=message,
                to=self.phone,
                from_=settings.TWILIO_FROM_NUMBER,
            )

            return response.sid

        if message and settings.SMS_SERVICE == 'Plivo':
            client = PlivoRestClient(
                settings.PLIVO_AUTH_ID,
                settings.PLIVO_AUTH_TOKEN
            )

            response = client.send_message({
                'src': settings.PLIVO_FROM_NUMBER,
                'dst': self.phone[1:], # drop the + before country code
                'text': message,
            })

            return response

        if message and settings.SMS_SERVICE == 'Debug':
            print message
            return True

        if message and settings.SMS_SERVICE == 'Primafon':
            res = requests.post(
                'http://sms.k8s.inonit.no/api/v0/messages/',
                json={
                    'to': self.phone[1:],
                    'body': message,
                },
                headers={
                    'Authorization':
                    'Token %s' % settings.PRIMAFON_KEY,
                })

            res.raise_for_status()
            return True

    def send_email(self, subject=None, message=None, html_message=None):
        if subject and (message or html_message):
            subject = settings.EMAIL_SUBJECT_PREFIX + subject

            email = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email]
            )

            if html_message:
                email.attach_alternative(html_message, 'text/html')

            return email.send()

    def generate_login_link(self):
        '''Generates a login link URL'''

        current_site = Site.objects.get_current()

        link = '%(protocol)s://%(domain)s%(link)s' % {
            'link': reverse(
                'login_via_email',
                kwargs={
                    'user_id': self.id,
                    'token': token_generator.make_token(self.id),
                }
            ),
            'protocol': 'https' if settings.USE_HTTPS else 'http',
            'domain': current_site.domain,
        }

        return link

    def send_login_link(self):
        '''Sends user login link via email templates'''

        subject = unicode(_("Today's login link"))

        html_template = get_template('email/login_link.html')
        text_template = get_template('email/login_link.txt')

        current_site = Site.objects.get_current()

        manual_login = '%s://%s%s' % (
            'https' if settings.USE_HTTPS else 'http',
            current_site.domain,
            reverse('login'),
        )

        context = {
            'link': self.generate_login_link(),
            'manual_login': manual_login,
            'site_name': current_site.name,
        }

        text_content = text_template.render(Context(context))
        html_content = html_template.render(Context(context))

        self.send_email(
            subject=subject,
            message=text_content,
            html_message=html_content
        )

    def register(self):
        '''
        Registration is not needed for a registered user
        (see StatefulAnonymousUser)
        '''
        return self, False

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class StatefulAnonymousUser(AnonymousUser):
    '''
    An AnonymousUser variant that retains user data in a session,
    and can be converted to a full user.
    '''

    def __init__(self, session):
        self.session = session
        self.data = session.get('user_data', {})

    def save(self):
        '''
        Save user data to session
        and retain as long as the session object is retained.
        '''
        self.session['user_data'] = self.data

    def register(self):
        '''
        Convert the StatefulAnonymousUser to a full User.
        Assumes at least password is already written to user data.
        '''
        password = self.data['password']
        email = self.data['email']
        phone = self.data['phone']

        user = User.objects.create_user(None, password, email, phone, data=self.data)

        try:
            del self.data['password']
            del self.data['email']
            del self.data['phone']
        except:
            pass

        User.objects.filter(id=user.id).update(data=self.data)

        return user, True

    def send_email(self, subject=None, message=None, html_message=None):
        '''
        Not implemented for an AnonymousUser,
        but pass rather than raise an exception
        '''
        pass

    def send_sms(self, message=None):
        '''
        Not implemented for an AnonymousUser,
        but pass rather than raise an exception
        '''
        pass
