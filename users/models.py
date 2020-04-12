from __future__ import unicode_literals
from __future__ import print_function
from builtins import str
from builtins import object
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, AnonymousUser
from django.contrib.sites.models import Site
from django.core.mail.message import EmailMultiAlternatives
from django.urls import reverse
from django.db import models, IntegrityError
from django.template import Context
from django.template.loader import get_template

from collections import OrderedDict
from jsonfield import JSONField
from plivo import RestClient as PlivoRestClient
from tokens.tokens import token_generator
from twilio.rest import Client
import requests


class UserManager(BaseUserManager):
    '''Custom User model Manager'''

    def create_user(self, id, password, email, phone, data=None):
        user = self.model()
        user.set_password(password)
        user.email = email
        if phone:
            # verify it's unique
            if User.objects.filter(phone=phone).count():
                raise IntegrityError()

        user.phone = phone
        if data:
            user.data = data
        user.save()
        return user

    def create_superuser(self, id, password, email='', phone=''):
        user = self.create_user(id=id, password=password, email=email, phone=phone)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User, identified by ID and password'''

    email = models.EmailField(_('e-mail address'), max_length=254, unique=True)
    phone = models.CharField(_('phone number'), max_length=32, unique=False, null=True)

    is_staff = models.BooleanField(_('staff status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)
    is_therapist = models.BooleanField('is therapist', default=False)
    therapist = models.ForeignKey('self', verbose_name='therapist', related_name='patients',
                                  on_delete=models.SET_NULL, null=True, blank=True)
    program_restrictions = models.ManyToManyField(
        to='system.Program', blank=True,
        verbose_name=_('program restrictions'),
        help_text=_('Staff user has limited access only to the chosen Programs (and related data). '
                    'If no Programs are chosen, there is no restriction.'),
        related_name='user_restriction_set',
        related_query_name='user_restriction'
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True, editable=False)

    token = models.CharField(_('token'), max_length=64, blank=True, editable=False)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default={})

    objects = UserManager()

    USERNAME_FIELD = 'email'

    @property
    def username(self):
        # return _('User %i' % self.id)
        return self.email

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
        if not self.phone or len(self.phone) < 11:  # 11 character phone number +4712345678 (norway)
            return False

        if message and settings.SMS_SERVICE == 'Twilio':
            client = Client(
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
                'dst': self.phone[1:],  # drop the + before country code
                'text': message,
            })

            return response

        if message and settings.SMS_SERVICE == 'Console':
            print(message)
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

    def send_email(self, subject=None, message=None, html_message=None, **kwargs):
        if subject and (message or html_message):

            pdfs = kwargs.get('pdfs', [])

            current_site = Site.objects.get_current()
            if hasattr(current_site, 'program'):
                print(current_site.program)
                subject = '[%s] %s' % (current_site.program.title, subject)
                from_email = current_site.program.from_email or settings.DEFAULT_FROM_EMAIL
            else:
                subject = settings.EMAIL_SUBJECT_PREFIX + subject
                from_email = settings.DEFAULT_FROM_EMAIL

            email = EmailMultiAlternatives(
                subject,
                message,
                from_email,
                [self.email]
            )

            if html_message:
                email.attach_alternative(html_message, 'text/html')

            for pdf in pdfs:
                email.attach_alternative(pdf, 'application/pdf')

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

        subject = str(_("Today's login link"))

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

        text_content = text_template.render(context)
        html_content = html_template.render(context)

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

    @staticmethod
    def _get_chapter_key(chapter_id):
        return "chapter_%s" % str(chapter_id)

    @staticmethod
    def _get_module_key(module_id):
        return "module_%s" % str(module_id)

    def register_chapter_to_page(self, page):
        if page.chapter is not None:
            key = User._get_chapter_key(page.chapter.id)
            self.data[key] = page.id
            module_key = User._get_module_key(page.chapter.module.id)
            self.data[module_key] = page.chapter.id

    def get_page_id_by_chapter(self, chapter_id):
        if not str(chapter_id).isnumeric():
            return None
        chapter_id = int(chapter_id)
        if chapter_id <= 0:
            return None
        key = User._get_chapter_key(chapter_id)
        if key in self.data:
            return self.data[key]
        return None

    def is_module_enabled(self, module_id):
        if not str(module_id).isnumeric():
            return False
        module_id = int(module_id)
        if module_id <= 0:
            return False
        key = User._get_module_key(module_id)
        return key in self.data

    def get_modules(self):
        result = []
        current_site = Site.objects.get_current()
        if hasattr(current_site, 'program'):
            program_modules = current_site.program.module_set.all()
            for module in program_modules:
                result.append({"name": module.display_title,
                               "id": module.id,
                               "is_enabled": self.is_module_enabled(module.id)})
        else:
            return []

        return result

    def get_chapter_by_module(self, module_id):
        module_key = User._get_module_key(module_id)
        if module_key not in self.data:
            return None
        return self.data[module_key]

    def __str__(self):
        return '%s' % self.id

    class Meta(object):
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
        phone = self.data['phone'] if 'phone' in self.data else None

        del self.data['password']
        del self.data['email']
        if 'phone' in self.data:
            del self.data['phone']

        user = User.objects.create_user(None, password, email, phone, data=self.data)

        return user, True

    def send_email(self, subject=None, message=None, html_message=None, **kwargs):
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
