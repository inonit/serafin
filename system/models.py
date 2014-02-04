from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from signals import schedule_part, reschedule_part, revoke_part
#from system.system import Stuff

class Program(object):
    '''A top level model for a separate Program, having one or more parts'''

    title = models.CharField(_('program title'), max_length=64)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = _('program')
        verbose_name_plural = _('programs')


class Part(models.Model):
    '''A program Part, with layout through a Graph object'''

    title = models.CharField(_('part title'), max_length=64, blank=True)

    program = models.ForeignKey(Program, verbose_name=_('program'))
    start_time = models.DateTimeField(_('start_time'), null=True, blank=True)
    end_time = models.DateTimeField(_('end_time'), null=True, blank=True)

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


class Page(models.Model):
    '''An ordered collection of Content to be shown together as a Page'''

    title = models.CharField(_('page title'), max_length=64, blank=True)

    # node_object = reference to Node object

    def __unicode__(self):
        return self.title or _('Page %s' % self.id)

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')


class Pagelet(models.Model):
    '''Ordered relation of Content belonging to a Page'''

    page = models.ForeignKey(Page, verbose_name=_('page'))
    content = models.ForeignKey('content.Content', verbose_name=_('content'))
    order = models.PositiveSmallIntegerField(_('order'), default=0)

    def __unicode__(self):
        return '%s, %s' % (self.page, self.content)

    class Meta:
        ordering = ['order']
        verbose_name = _('pagelet')
        verbose_name_plural = _('pagelets')
