from __future__ import unicode_literals

import datetime
from builtins import object
from time import sleep

from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from huey.contrib.djhuey import HUEY as huey
from huey.constants import EmptyData
import pickle


class TaskManager(models.Manager):
    def create_task(self, sender, domain, time, task, args, action, subject=None):
        task_ref = task.schedule(
            args=args,
            eta=timezone.localtime(time).replace(tzinfo=None)
        )

        task = Task()
        task.sender = sender
        task.domain = domain
        task.time = time
        task.action = action
        task.task = task_ref

        if subject:
            task.subject = subject

        task.save()

        return task


class Task(models.Model):
    '''A model to keep track of Huey task management in the admin interface'''

    content_type = models.ForeignKey(ContentType, verbose_name=_('sender'), on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('content_type', 'object_id')
    subject = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('subject'), null=True, blank=True,
                                on_delete=models.CASCADE)

    domain = models.CharField(_('domain'), max_length=32)
    action = models.CharField(_('action'), max_length=255, blank=True)
    task_id = models.CharField(_('task'), max_length=255)

    time = models.DateTimeField(_('time'))

    objects = TaskManager()

    def __unicode__(self):
        return _('%(time)s: %(sender)s, %(action)s') % {
            'time': self.time,
            'sender': self.sender,
            'action': self.action,
        }

    def __str__(self):
        return _('%(time)s: %(sender)s, %(action)s') % {
            'time': self.time,
            'sender': self.sender,
            'action': self.action,
        }

    class Meta(object):
        verbose_name = _('task')
        verbose_name_plural = _('tasks')

    @property
    def result(self):
        return self.task

    @property
    def task(self):
        '''Returns the task result and preserves it'''
        if self.task_id:
            return huey.result(self.task_id, preserve=True)

    @property
    def result_block(self):
        if self.task_id:
            return huey.result(self.task_id, blocking=True, preserve=True)

    @task.setter
    def task(self, task):
        self.task_id = task.task.id

    def revoke(self):
        '''Revokes this task and returns its result'''

        if self.task_id:
            result = None
            try:
                result = huey.result(self.task_id, preserve=True)
            except:
                pass
            huey.revoke_by_id(self.task_id)
            return result

    def reschedule(self, task, args, time):
        '''Revokes and reschedules given task function, returns result, if any'''

        result = self.revoke()
        task_ref = task.schedule(
            args=args,
            eta=timezone.localtime(time).replace(tzinfo=None)
        )
        self.task = task_ref
        self.time = time
        self.save()

        return result
