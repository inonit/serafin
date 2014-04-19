from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.core.urlresolvers import reverse
from jsonfield import JSONField
from collections import OrderedDict


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

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')

    def __unicode__(self):
        return self.title


class Part(models.Model):
    '''A program Part, with layout and logic encoded in JSON'''

    title = models.CharField(_('title'), max_length=64, blank=True, unique=True)
    program = models.ForeignKey(Program, verbose_name=_('program'))
    admin_note = models.TextField(_('admin note'), blank=True)

    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    vars_used = models.ManyToManyField(Variable, editable=False)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')

    def __unicode__(self):
        return self.title or _('Part %s' % self.id)

    def get_absolute_url(self):
        return reverse('part', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super(Part, self).save(*args, **kwargs)

        self.vars_used = []
        for edge in self.data['edges']:
            for condition in edge['conditions']:

                variable, created = Variable.objects.get_or_create(name=condition.variable_name)
                if created:
                    variable.save()

                self.vars_used.add(variable)


class Page(models.Model):
    '''An ordered collection of JSON content to be shown together as a Page'''

    title = models.CharField(_('title'), max_length=64, blank=True, unique=True)
    part = models.ForeignKey(Part, verbose_name=_('part'), null=True, blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    vars_used = models.ManyToManyField(Variable, editable=False)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')

    def __unicode__(self):
        return self.title or _('Page %s' % self.id)

    def get_absolute_url(self):
        return reverse('page', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super(Page, self).save(*args, **kwargs)

        self.vars_used = []
        for pagelet in self.data:
            if pagelet['content_type'] == 'form':
                for field in pagelet['content']:

                    variable, created = Variable.objects.get_or_create(name=field.variable_name)
                    if created:
                        variable.save()

                    self.vars_used.add(variable)
