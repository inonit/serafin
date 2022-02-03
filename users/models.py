from __future__ import unicode_literals
from __future__ import print_function

import logging
from builtins import str
from builtins import object
from smtplib import SMTPDataError

from django.db.models import Q
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

from system.models import ProgramUserAccess, Session, Variable
from tokens.tokens import token_generator
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from huey.contrib.djhuey import task
import requests

logger = logging.getLogger(__name__)


class UserManager(BaseUserManager):
    '''Custom User model Manager'''

    def create_user(self, password, email, phone, secondary_phone=None, data=None):
        user = self.model()
        user.set_password(password)
        user.email = email
        if phone:
            # verify it's unique
            if User.objects.filter(Q(phone=phone) | Q(secondary_phone=phone)).count():
                raise IntegrityError()
        user.phone = phone

        if secondary_phone:
            if User.objects.filter(Q(phone=secondary_phone) | Q(secondary_phone=secondary_phone)).count():
                raise IntegrityError()
        user.secondary_phone = secondary_phone

        if data:
            user.data = data
        user.save()
        return user

    def create_superuser(self, password, email='', phone=''):
        user = self.create_user(password=password, email=email, phone=phone)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User, identified by ID and password'''

    email = models.EmailField(_('e-mail address'), max_length=254, unique=True)
    phone = models.CharField(_('phone number'), max_length=32, unique=False, null=True)
    secondary_phone = models.CharField(_('secondary phone number'), max_length=32, unique=False, null=True)

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
    DELETE_MESSAGE_AFTER_SECONDS = 10

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

    @property
    def password_change_required(self):
        change_password_key = 'force_change_password'
        if self.data and change_password_key in self.data:
            password_change_required = self.data[change_password_key]
            return password_change_required
        return False

    def password_changed(self):
        change_password_key = 'force_change_password'
        if self.data:
            self.data[change_password_key] = False
            self.save()

    def send_sms(self, message=None, is_whatsapp=False):
        results = []
        phone_numbers = [self.phone, self.secondary_phone]
        for phone_number in phone_numbers:
            if not phone_number or len(phone_number) < 11: # 11 character phone number +4712345678 (norway)
                results.append(False)
                continue

            if message and settings.SMS_SERVICE == 'Twilio':
                client = Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN
                )

                if is_whatsapp:
                    response = client.messages.create(
                        body=message,
                        to="whatsapp:" + phone_number,
                        from_="whatsapp:" + settings.TWILIO_WHATSAPP_FROM_NUMBER,
                    )
                else:
                    response = client.messages.create(
                        body=message,
                        to=phone_number,
                        from_=settings.TWILIO_FROM_NUMBER,
                    )

                results.append(response.sid)
                logger.info(f'Create message {response.sid} with status {response.status}')
                User.delete_twilio_message.schedule((response.sid,), delay=User.DELETE_MESSAGE_AFTER_SECONDS)

            if message and settings.SMS_SERVICE == 'Plivo':
                client = PlivoRestClient(
                    settings.PLIVO_AUTH_ID,
                    settings.PLIVO_AUTH_TOKEN
                )

                response = client.send_message({
                    'src': settings.PLIVO_FROM_NUMBER,
                    'dst': phone_number[1:],  # drop the + before country code
                    'text': message,
                })

                results.append(response)

            if message and settings.SMS_SERVICE == 'Console':
                print(message)
                results.append(True)

            if message and settings.SMS_SERVICE == 'Primafon':
                res = requests.post(
                    'http://sms.k8s.inonit.no/api/v0/messages/',
                    json={
                        'to': phone_number[1:],
                        'body': message,
                    },
                    headers={
                        'Authorization':
                            'Token %s' % settings.PRIMAFON_KEY,
                    })

                res.raise_for_status()
                results.append(True)

        return results[0] or results[1]

    @staticmethod
    @task()
    def delete_twilio_message(message_id, current_retry=0):
        # ~ 15 days
        max_retries = 23
        retries_interval_options_seconds = [30, 60, 300, 600, 3600, 18000, 86400]
        retry_in_seconds = retries_interval_options_seconds[
            min(current_retry, len(retries_interval_options_seconds) - 1)]
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        try:
            message = client.messages(message_id).fetch()
        except TwilioRestException:
            logger.exception(f'Could not fetch message {message_id} for delete')
            return
        logger.info(f'Message {message_id} status: {message.status}')
        if message.status in ['sent', 'delivered', 'read', 'undelivered', 'failed']:
            if message.status in ['undelivered', 'failed']:
                logger.warning(
                    f'Error while sending message {message_id}: {message.error_message} ({message.error_code})')
            try:
                client.messages(message_id).update(body='')
                logger.info(f'Message {message_id} deleted')
            except TwilioRestException:
                if current_retry + 1 < max_retries:
                    logger.exception(
                        f'Could not delete message {message_id} after {current_retry} retries, '
                        f'reschedule message delete in {retry_in_seconds} seconds...')
                    User.delete_twilio_message.schedule((message_id, current_retry + 1), delay=retry_in_seconds)
                else:
                    logger.error(f'Could not delete message {message_id} after {current_retry}')
        elif current_retry + 1 < max_retries:
            logger.info(
                f'Reschedule message delete {message_id} '
                f'after {current_retry} retries in {retry_in_seconds} seconds...')
            User.delete_twilio_message.schedule((message_id, current_retry + 1), delay=retry_in_seconds)
        else:
            logger.error(f'Could not delete message {message_id} after {current_retry} retries')

    def send_email(self, subject=None, message=None, html_message=None, **kwargs):
        if subject and (message or html_message):

            pdfs = kwargs.get('pdfs', [])

            user_program = self.get_first_program()
            current_site = Site.objects.get_current()
            if hasattr(current_site, 'program'):
                print(current_site.program)
                subject = '[%s] %s' % (current_site.program.display_title, subject)
                from_email = current_site.program.from_email or settings.DEFAULT_FROM_EMAIL
            elif user_program:
                subject = '[%s] %s' % (user_program.display_title, subject)
                from_email = user_program.from_email or settings.DEFAULT_FROM_EMAIL
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

            response = None
            try:
                response = email.send()
            except SMTPDataError:
                logger.exception('error while sending email')

            return response

    @staticmethod
    def generate_session_link():
        """Generate a url link to session"""
        current_site = Site.objects.get_current()

        link = '%(protocol)s://%(domain)s%(link)s' % {
            'link': reverse('content'),
            'protocol': 'https' if settings.USE_HTTPS else 'http',
            'domain': current_site.domain
        }

        return link

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
            'link': self.generate_session_link(),
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

    def send_new_message_notification(self):
        '''Sends user new message notification with link'''

        subject = str(_("You have a new message"))
        html_template = get_template('email/new_message.html')
        text_template = get_template('email/new_message.txt')

        current_site = Site.objects.get_current()

        mytherapist_link = '%s://%s%s' % (
            'https' if settings.USE_HTTPS else 'http',
            current_site.domain,
            reverse('mytherapist'),
        )

        context = {
            'my_therapist': mytherapist_link,
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
        # we assume user has only one program
        session_id = self.data.get('session')
        if not session_id:
            return []
        session = Session.objects.get(id=session_id)
        if not session:
            return []
        program = session.program
        if program:
            program_modules = program.module_set.all()
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

    def get_first_program_user_access(self, program=None):
        if program:
            program_user_access = ProgramUserAccess.objects.filter(user=self, program=program).first()
        else:
            program_user_access = ProgramUserAccess.objects.filter(user=self).first()
        return program_user_access

    def get_first_program(self):
        program_user_access = self.get_first_program_user_access()
        if program_user_access is not None:
            return program_user_access.program
        return None

    get_first_program.short_description = 'Program'

    def get_pre_variable_value_for_log(self, variable_name):
        def recursive_stripe(v):
            if isinstance(v, list):
                return '[' + ', '.join([recursive_stripe(x) for x in v]) + ']'
            else:
                if isinstance(v, str):
                    return v.strip()
                else:
                    return str(v)

        pre_value = self.data.get(variable_name, '')
        if isinstance(pre_value, list):
            pre_value = ', '.join([recursive_stripe(v) for v in pre_value])

        return pre_value

    def get_tools(self):
        """
        return list of Tools asset {'url': <>, 'type': <file/video/audio>, 'title': <>}
        """

        tools = self.data.get('tools', [])
        return tools

    def set_variable_value(self, variable_name, variable_value):
        """
        add/set value to a variable in user's data
        """
        User.set_variable_value_helper(self, variable_name, variable_value)


    @staticmethod
    def set_variable_value_helper(user, variable_name, variable_value):
        if Variable.is_array_variable(variable_name):
            if variable_name in user.data and isinstance(user.data[variable_name], list):
                user.data[variable_name].append(variable_value)
                max_entries = Variable.array_max_entries(variable_name)
                while max_entries and len(user.data[variable_name]) > max_entries:
                    user.data[variable_name].pop(0)
            else:
                user.data[variable_name] = [variable_value]
        else:
            user.data[variable_name] = variable_value

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
        secondary_phone = self.data['secondary_phone'] if 'secondary_phone' in self.data else None

        del self.data['password']
        del self.data['email']
        if 'phone' in self.data:
            del self.data['phone']
        if 'secondary_phone' in self.data:
            del self.data['secondary_phone']

        user = User.objects.create_user(password, email, phone, secondary_phone=secondary_phone, data=self.data)

        return user, True

    def send_email(self, subject=None, message=None, html_message=None, **kwargs):
        '''
        Not implemented for an AnonymousUser,
        but pass rather than raise an exception
        '''
        pass

    def send_sms(self, message=None, is_whatsapp=False):
        '''
        Not implemented for an AnonymousUser,
        but pass rather than raise an exception
        '''
        pass

    def get_pre_variable_value_for_log(self, variable_name):
        return None

    def set_variable_value(self, variable_name, variable_value):
        """
        add/set value to a variable in user's data
        """
        User.set_variable_value_helper(self, variable_name, variable_value)
