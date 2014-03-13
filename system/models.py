from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from signals import schedule_part, reschedule_part, revoke_part
#from system.system import Stuff
from content.models import Content


class Program(models.Model):
    '''A top level model for a separate Program, having one or more parts'''

    title = models.CharField(_('title'), max_length=64)

    #start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    #end_time = models.DateTimeField(_('end time'), null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')


class Part(models.Model):
    '''A program Part, with layout through a Graph object'''

    title = models.CharField(_('title'), max_length=64, blank=True)

    program = models.ForeignKey(Program, verbose_name=_('program'))
    start_time = models.DateTimeField(_('start time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end time'), null=True, blank=True)

    #created_at = models.DateTimeField(_('created at'), null=True, blank=True)
    #changed_at = models.DateTimeField(_('changed at'), null=True, blank=True)

    # graph_object = reference to Graph object

    def schedule():
        schedule_part.send()

    def reschedule():
        reschedule_part.send()

    def revoke():
        revoke_part.send()

    def __unicode__(self):
        return self.title or _('Part %s' % self.id)

    class Meta:
        verbose_name = _('part')
        verbose_name_plural = _('parts')


class Page(Content):
    '''An ordered collection of Content to be shown together as a Page'''

    title = models.CharField(_('title'), max_length=64, blank=True)
    part = models.ForeignKey(Part, verbose_name=_('part'), null=True, blank=True)

    # node_object = reference to Node object

    def __unicode__(self):
        return self.title or _('Page %s' % self.id)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')
