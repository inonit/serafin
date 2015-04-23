# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import datetime
import mistune
import random

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField
from collections import OrderedDict
from serafin.utils import *


class Variable(models.Model):
    '''A variable model allowing different options'''

    name = models.CharField(_('name'), max_length=64, unique=True)
    display_name = models.CharField(_('display name'), max_length=64, blank=True, default='')
    admin_note = models.TextField(_('admin note'), blank=True)
    program = models.ForeignKey('Program', verbose_name=_('program'), null=True)
    value = models.CharField(_('initial value'), max_length=32, blank=True, default='')
    user_editable = models.BooleanField(_('user editable'), default=False)
    RANDOM_TYPES = (
        ('boolean', _('boolean')),
        ('numeric', _('numeric')),
        ('string', _('string')),
    )
    random_type = models.CharField(_('randomization type'), max_length=16, choices=RANDOM_TYPES, null=True, blank=True)
    randomize_once = models.BooleanField(_('randomize once'), default=False)
    range_min = models.IntegerField(_('range min (inclusive)'), null=True, blank=True)
    range_max = models.IntegerField(_('range max (inclusive)'), null=True, blank=True)
    random_set = models.TextField(_('random string set'), blank=True)

    class Meta:
        verbose_name = _('variable')
        verbose_name_plural = _('variables')
        ordering = ('display_name', 'name', 'value')

    def __unicode__(self):
        return self.name

    def get_value(self):
        random.seed()

        if self.random_type == 'boolean':
            return random.choice([True, False])

        elif self.random_type == 'numeric':
            range_min = self.range_min or 0
            range_max = self.range_max or 0
            return random.randint(range_min, range_max)

        elif self.random_type == 'string':
            try:
                random_set = [item.strip() for item in self.random_set.split(',')]
                return random.choice(random_set)
            except:
                return ''
        else:
            return self.value


class Program(models.Model):
    '''A top level model for a separate Program, having one or more sessions'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    admin_note = models.TextField(_('admin note'), blank=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('users'), through='ProgramUserAccess')

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')

    def __unicode__(self):
        return self.title

    def enroll(self, user, start_time=None, time_factor=None):
        ProgramUserAccess.objects.create(
            program=self,
            user=user,
            start_time=start_time or timezone.now(),
            time_factor=time_factor or 1.0
        )
        return True


class ProgramUserAccess(models.Model):
    '''
    A relational model that allows Users to have access to a Program,
    with their own start time and time factor
    '''

    program = models.ForeignKey('Program', verbose_name=_('program'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    start_time = models.DateTimeField(_('start time'), default=timezone.now)
    time_factor = models.DecimalField(_('time factor'), default=1.0, max_digits=5, decimal_places=3)

    class Meta:
        verbose_name = _('user access')
        verbose_name_plural = _('user accesses')

    def __unicode__(self):
        return '%s: %s' % (self.program, self.user.__unicode__())


class Session(models.Model):
    '''A program Session, with layout and logic encoded in JSON'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    route_slug = models.CharField(_('route slug'), max_length=64, null=True, unique=True, default=None)
    is_open = models.BooleanField(_('is open'), default=False)
    program = models.ForeignKey('Program', verbose_name=_('program'))
    content = models.ManyToManyField('Content', verbose_name=_('content'), null=True, blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    TIME_UNITS = (
        ('hours', _('hours')),
        ('days', _('days')),
    )
    start_time_delta = models.IntegerField(_('start time delta'), default=0)
    start_time_unit = models.CharField(_('start time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    end_time_delta = models.IntegerField(_('end time delta'), default=0)
    end_time_unit = models.CharField(_('end time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    start_time = models.DateTimeField(_('first start time'), null=True, blank=True)
    scheduled = models.BooleanField(_('scheduled'), default=False)
    trigger_login = models.BooleanField(_('trigger login'), default=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    class Meta:
        verbose_name = _('session')
        verbose_name_plural = _('sessions')

    def __unicode__(self):
        return self.title or _('Session %s' % self.id)

    def get_absolute_url(self):
        return '%s?session_id=%i' % (
            reverse('content'),
            self.id,
        )

    def clean(self):
        for edge in self.data['edges']:
            for condition in edge['conditions']:
                if not condition['var_name']:
                    raise ValidationError(_('A variable name is required for all conditions'))
                try:
                    variable = Variable.objects.get(name=condition['var_name'])
                except Variable.DoesNotExist:
                    if not condition['var_name'] in [var['name'] for var in settings.RESERVED_VARIABLES]:
                        raise ValidationError(
                            _('Could not find Variable `%(var_name)s`. Please make sure all variables are predefined.') % {
                                'var_name': condition['var_name']
                            }
                        )

    def save(self, *args, **kwargs):
        first_useraccess = self.program.programuseraccess_set.order_by('start_time').first()
        if first_useraccess and self.scheduled:
            self.start_time = self.get_start_time(
                first_useraccess.start_time,
                first_useraccess.time_factor
            )
        else:
            self.start_time = None

        super(Session, self).save(*args, **kwargs)

        self.content = []
        for node in self.data['nodes']:
            try:
                self.content.add(node['ref_id'])
            except:
                pass

    def get_start_time(self, start_time, time_factor):
        kwargs = {
            self.start_time_unit: float(self.start_time_delta * time_factor)
        }
        timedelta = datetime.timedelta(**kwargs)
        return start_time + timedelta


class Content(models.Model):
    '''An ordered collection of JSON content'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    display_title = models.CharField(_('display title'), max_length=64)
    content_type = models.CharField(_('content type'), max_length=32, editable=False)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='[]')

    class Meta:
        verbose_name = _('content')
        verbose_name_plural = _('contents')

    def __unicode__(self):
        return self.title or '%s %s' % (self._meta.verbose_name, self.id)

    def get_absolute_url(self):
        return '%s?page_id=%i' % (
            reverse('content'),
            self.id,
        )


class PageManager(models.Manager):
    def get_queryset(self):
        return super(PageManager, self).get_queryset().filter(content_type='page')


class Page(Content):
    '''An ordered collection of JSON content to be shown together as a Page'''

    objects = PageManager()

    class Meta:
        proxy = True
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __init__(self, *args, **kwargs):
        super(Page, self).__init__(*args, **kwargs)
        self.content_type = 'page'

    def clean(self):
        for pagelet in self.data:
            if pagelet['content_type'] == 'form':
                for field in pagelet['content']:
                    if not field['variable_name']:
                        raise ValidationError(_('A variable name is required for all fields'))
                    try:
                        variable = Variable.objects.get(name=field['variable_name'])
                    except Variable.DoesNotExist:
                        if not field['variable_name'] in [var['name'] for var in settings.RESERVED_VARIABLES]:
                            raise ValidationError(
                                _('Could not find Variable `%(var_name)s`. Please make sure all variables are predefined.') % {
                                    'var_name': field['variable_name']
                                }
                            )

    def update_html(self, user):
        for pagelet in self.data:
            if pagelet['content_type'] in ['text', 'toggle']:
                content = pagelet.get('content')
                content = remove_comments(content)
                content, pagelet['variables'] = live_variable_replace(user, content)
                pagelet['content'] = mistune.markdown(content)

            if pagelet['content_type'] == 'conditionalset':
                from system.engine import Engine

                for text in pagelet['content']:

                    conditions = text.get('conditions')
                    passing = Engine.check_conditions(conditions, user, True)

                    if passing:
                        content = text.get('content')
                        content = remove_comments(content)
                        content, pagelet['variables'] = live_variable_replace(user, content)
                        text['content'] = mistune.markdown(content)
                    else:
                        text['content'] = ''


class EmailManager(models.Manager):
    def get_queryset(self):
        return super(EmailManager, self).get_queryset().filter(content_type='email')


class Email(Content):
    '''A model for e-mail content'''

    objects = EmailManager()

    class Meta:
        proxy = True
        verbose_name = _('e-mail')
        verbose_name_plural = _('e-mails')

    def __init__(self, *args, **kwargs):
        super(Email, self).__init__(*args, **kwargs)
        self.content_type = 'email'

    def send(self, user):
        message = self.data[0].get('content')
        message = process_session_links(user, message)
        message = remove_comments(message)
        message = variable_replace(user, message)
        html_message = mistune.markdown(message)

        user.send_email(
            subject=self.display_title,
            message=message,
            html_message=html_message
        )


class SMSManager(models.Manager):
    def get_queryset(self):
        return super(SMSManager, self).get_queryset().filter(content_type='sms')


class SMS(Content):
    '''A model for SMS content'''

    objects = SMSManager()

    class Meta:
        proxy = True
        verbose_name = _('SMS')
        verbose_name_plural = _('SMSs')

    def __init__(self, *args, **kwargs):
        super(SMS, self).__init__(*args, **kwargs)
        self.content_type = 'sms'
        self.display_title = ''

    def send(self, user):
        message = self.data[0].get('content')
        message = process_session_links(user, message)
        message = process_reply_variables(user, message)
        message = remove_comments(message)
        message = variable_replace(user, message)

        user.send_sms(
            message=message
        )
