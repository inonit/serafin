from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings


class Event(models.Model):
    '''A log event'''

    time = models.DateTimeField(_('time'), auto_now_add=True)
    domain = models.CharField(_('domain'), max_length=32)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('actor'))
    variable = models.CharField(_('variable'), max_length=64)
    pre_value = models.CharField(_('pre value'), max_length=1024, blank=True)
    post_value = models.CharField(_('post value'), max_length=1024, blank=True)

    def __unicode__(self):
        return '%s, %s' % (self.domain, self.time)

    class Meta:
        verbose_name = _('event')
        verbose_name_plural = _('events')
