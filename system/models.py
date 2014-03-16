from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.core.urlresolvers import reverse
from jsonfield import JSONField
from collections import OrderedDict


class Program(models.Model):
    '''A top level model for a separate Program, having one or more parts'''

    title = models.CharField(_('title'), max_length=64)
    admin_note = models.TextField(_('admin note'), blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')


class Part(models.Model):
    '''A program Part, with layout through a Graph object'''

    title = models.CharField(_('title'), max_length=64, blank=True)
    program = models.ForeignKey(Program, verbose_name=_('program'))
    admin_note = models.TextField(_('admin note'), blank=True)

    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    def get_absolute_url(self):
        return reverse('part', args=[str(self.id)])

    def __unicode__(self):
        return self.title or _('Part %s' % self.id)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')


class Page(models.Model):
    '''An ordered collection of Content to be shown together as a Page'''

    title = models.CharField(_('title'), max_length=64, blank=True)
    part = models.ForeignKey(Part, verbose_name=_('part'), null=True, blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

    def get_absolute_url(self):
        return reverse('page', args=[str(self.id)])

    def __unicode__(self):
        return self.title or _('Page %s' % self.id)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
