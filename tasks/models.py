from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from picklefield.fields import PickledObjectField
from huey.djhuey import crontab, task


class Task(models.Model):
    '''A model to keep track of Huey task management in the admin interface'''

    content_type = models.ForeignKey(ContentType, verbose_name=_('sender'))
    object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(_('action'), max_length=255)
    task = PickledObjectField()

    time = models.DateTimeField(_('time'))

    def __unicode__(self):
        return _('%(time)s: %(sender)s, %(action)s') % {
            'time': self.time,
            'sender': self.sender,
            'action': self.action,
        }

    class Meta:
        verbose_name = _('task')
        verbose_name_plural = _('tasks')
