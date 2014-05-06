from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.core.urlresolvers import reverse
from django.utils import timezone
from jsonfield import JSONField
from collections import OrderedDict
import datetime


class Variable(models.Model):
    '''A variable reference for efficient lookup'''

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
    '''A top level model for a separate Program, having one or more parts'''

    title = models.CharField(_('title'), max_length=64, unique=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    start_time = models.DateTimeField(_('start time'), default=lambda: timezone.localtime(timezone.now()))
    time_factor = models.DecimalField(_('time factor'), default=1.0, max_digits=5, decimal_places=2)

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')

    def __unicode__(self):
        return self.title

    def save(self, *args, **kwargs):
        super(Program, self).save(*args, **kwargs)
        for part in self.part_set.all():
            part.save()


class Part(models.Model):
    '''A program Part, with layout and logic encoded in JSON'''

    title = models.CharField(_('title'), max_length=64, blank=True, unique=True)
    program = models.ForeignKey(Program, verbose_name=_('program'))
    admin_note = models.TextField(_('admin note'), blank=True)

    TIME_UNITS = (
        ('hours', _('hours')),
        ('days', _('days')),
    )
    start_time_delta = models.IntegerField(_('start time delta'), default=0)
    start_time_unit = models.CharField(_('start time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    end_time_delta = models.IntegerField(_('end time delta'), default=0)
    end_time_unit = models.CharField(_('end time unit'), max_length=32, choices=TIME_UNITS, default='hours')
    start_time = models.DateTimeField(_('start time'))

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    vars_used = models.ManyToManyField(Variable, editable=False)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')

    def __unicode__(self):
        return self.title or _('Part %s' % self.id)

    def get_absolute_url(self):
        return '%s?part_id=%i' % (
            reverse('content'),
            self.id,
        )

    def save(self, *args, **kwargs):
        self.start_time = self.get_start_time()

        self.vars_used = []
        for edge in self.data['edges']:
            for condition in edge['conditions']:

                variable, created = Variable.objects.get_or_create(name=condition['var_name'])
                if created:
                    variable.save()

                self.vars_used.add(variable)

        super(Part, self).save(*args, **kwargs)


    def get_start_time(self):
        kwargs = {
            self.start_time_unit: float(self.start_time_delta * self.program.time_factor)
        }
        timedelta = datetime.timedelta(**kwargs)
        return self.program.start_time + timedelta


class Page(models.Model):
    '''An ordered collection of JSON content to be shown together as a Page'''

    title = models.CharField(_('title'), max_length=64, blank=True, unique=True)
    parts = models.ManyToManyField(Part, verbose_name=_('parts'), null=True, blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    vars_used = models.ManyToManyField(Variable, editable=False)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __unicode__(self):
        return self.title or _('Page %s' % self.id)

    def get_absolute_url(self):
        return '%s?part_id=%i&page_id=%i' % (
            reverse('content'),
            self.part.id,
            self.id,
        )

    def save(self, *args, **kwargs):
        self.vars_used = []
        for pagelet in self.data:
            if pagelet['content_type'] == 'form':
                for field in pagelet['content']:

                    variable, created = Variable.objects.get_or_create(name=field['variable_name'])
                    if created:
                        variable.var_type = field['field_type']
                        variable.save()

                    self.vars_used.add(variable)

        super(Page, self).save(*args, **kwargs)


class SystemVariable(models.Model):
    '''A system-scope variable'''

    key = models.CharField(_('key'), max_length=64, primary_key=True)
    value = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    class Meta:
        verbose_name = _('system variable')
        verbose_name_plural = _('system variables')

    def __unicode__(self):
        return '%s: %s' % (self.key, self.value)
