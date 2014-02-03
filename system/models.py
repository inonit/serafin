from django.db import models


class Program(object):
    ''''''
    pass


class Part(object):
    '''A graph of Nodes connected by Edges describing the '''
    pass


class Node(object):
    ''''''
    pass


class Edge(object):
    ''''''
    pass


class BuildingBlock(object):
    '''A simplified collection of logical'''
    pass


class Page(models.Model):
    '''An ordered collection of Content to be shown together as a Page'''
    pass

    def __unicode__(self):
        return ''

    class Meta:
        verbose_name = _('page')
        verbose_name_plural = _('pages')


class Pagelet(models.Model):
    '''Ordered relation of Content belonging to a Page'''

    page = models.ForeignKey(Page, verbose_name=_('page'))
    content = models.ForeignKey('content.Content', verbose_name=_('content'))
    order = models.PositiveSmallIntegerField(_('order'), default=0)

    def __unicode__(self):
        return '%s' % (self.page, self.content)

    class Meta:
        ordering = ['order']
        verbose_name = _('pagelet')
        verbose_name_plural = _('pagelets')
