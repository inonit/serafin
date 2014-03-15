from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from huey.djhuey import HUEY as huey
from huey.utils import EmptyData
import pickle


class Task(models.Model):
    '''A model to keep track of Huey task management in the admin interface'''

    content_type = models.ForeignKey(ContentType, verbose_name=_('sender'))
    object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(_('action'), max_length=255, blank=True)
    task_id = models.CharField(_('task'), max_length=255)

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

    @property
    def task(self):
        if self.task_id:

            result = huey._get(self.task_id, peek=True)
            if result is not EmptyData:
                return pickle.loads(result)
            else:
                return None
        return None

    @task.setter
    def task(self, task):
        self.task_id = task.task.task_id

    def revoke(self):
        '''Revokes this task and returns its result'''

        if self.task_id:

            result = huey._get(self.task_id, peek=True)
            serialized = pickle.dumps((False, False))
            huey._put('r:%s' % self.task_id, serialized)

        return result
