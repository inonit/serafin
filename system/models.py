from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from jsonfield import JSONField
from collections import OrderedDict
from serafin.utils import user_data_replace, process_session_links
import datetime
import mistune


class Variable(models.Model):
    '''A variable reference for more efficient lookup'''

    name = models.CharField(_('name'), max_length=64, unique=True)
    VAR_TYPES = (
        ('numeric', _('numeric')),
        ('string', _('string')),
        ('text', _('text')),
        ('multiplechoice', _('multiple choice')),
        ('multipleselection', _('multiple selection')),
    )
    var_type = models.CharField(_('variable type'), max_length=32, choices=VAR_TYPES)

    class Meta:
        verbose_name = _('variable')
        verbose_name_plural = _('variables')

    def __unicode__(self):
        return self.name


class Program(models.Model):
    '''A top level model for a separate Program, having one or more sessions'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    users = models.ManyToManyField(settings.AUTH_USER_MODEL, verbose_name=_('users'), through='ProgramUserAccess')

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Program, self).save(*args, **kwargs)
        for session in self.session_set.all():
            session.save()


class ProgramUserAccess(models.Model):
    '''
    A relational model that allows Users to have access to a Program,
    with their own start time and time factor
    '''

    program = models.ForeignKey('Program', verbose_name=_('program'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    start_time = models.DateTimeField(_('start time'), default=lambda: timezone.localtime(timezone.now()))
    time_factor = models.DecimalField(_('time factor'), default=1.0, max_digits=5, decimal_places=3)

    class Meta:
        verbose_name = _('user access')
        verbose_name_plural = _('user accesses')

    def __unicode__(self):
        return '%s: %s' % (self.program, self.user.__unicode__())


class Session(models.Model):
    '''A program Session, with layout and logic encoded in JSON'''

    title = models.CharField(_('title'), max_length=64, unique=True)
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

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    vars_used = models.ManyToManyField('Variable', editable=False)

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

    def save(self, *args, **kwargs):
        first_useraccess = self.program.programuseraccess_set.order_by('start_time').first()
        if first_useraccess:
            self.start_time = self.get_start_time(
                first_useraccess.start_time,
                first_useraccess.time_factor
            )

        super(Session, self).save(*args, **kwargs)

        self.content = []
        for node in self.data['nodes']:
            try:
                self.content.add(node['ref_id'])
            except:
                pass

        self.vars_used = []
        for edge in self.data['edges']:
            for condition in edge['conditions']:

                variable, created = Variable.objects.get_or_create(
                    name=condition['var_name']
                )
                if created:
                    variable.save()

                self.vars_used.add(variable)

    def get_start_time(self, start_time, time_factor):
        kwargs = {
            self.start_time_unit: float(self.start_time_delta * time_factor)
        }
        timedelta = datetime.timedelta(**kwargs)
        return start_time + timedelta


class Content(models.Model):
    '''An ordered collection of JSON content'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    content_type = models.CharField(_('title'), max_length=32, editable=False)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='[]')

    vars_used = models.ManyToManyField('Variable', editable=False)

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

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)

        self.vars_used = []
        for pagelet in self.data:
            if pagelet['content_type'] == 'form':
                for field in pagelet['content']:

                    variable, created = Variable.objects.get_or_create(
                        name=field['variable_name']
                    )
                    if created:
                        variable.var_type = field['field_type']
                        variable.save()

                    self.vars_used.add(variable)

    def update_html(self, user):
        for pagelet in self.data:
            if pagelet['content_type'] in ['text', 'toggle']:
                content = pagelet.get('content')
                content = user_data_replace(
                    user,
                    content
                )
                pagelet['content'] = mistune.markdown(content)


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
        html_message = mistune.markdown(message)

        user.send_email(
            subject=self.title,
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

    def send(self, user):
        message = self.data[0].get('content')
        message = process_session_links(user, message)

        user.send_sms(
            message=message
        )
