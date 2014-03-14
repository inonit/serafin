from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.cache import get_cache
import hashlib

TERRIBLE_GLOBAL_CACHE_HACK = {}

class Task(models.Model):
    '''A model to keep track of Huey task management in the admin interface'''

    content_type = models.ForeignKey(ContentType, verbose_name=_('sender'))
    object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('content_type', 'object_id')

    action = models.CharField(_('action'), max_length=255)
    task = models.CharField(_('task'), max_length=255)

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

    def cache_task(self, task_reference):
        '''Caches a task reference for later retrieval and returns its hash'''
        global TERRIBLE_GLOBAL_CACHE_HACK

        task_hash = hashlib.md5(str(task_reference.__hash__())).hexdigest()

        #cache = get_cache('huey_tasks')
        #cache.set(task_hash, task_reference, timeout=None)
        #cache.close()

        TERRIBLE_GLOBAL_CACHE_HACK[task_hash] = task_reference

        return task_hash

    def revoke_cached_task(self, task_hash=None):
        '''Revokes a cached task from hash or self.task and returns its result'''

        #cache = get_cache('huey_tasks')
        #task_reference = cache.get(task_hash or self.task)

        result = None
        try:
            task_reference = TERRIBLE_GLOBAL_CACHE_HACK[task_hash]
            del TERRIBLE_GLOBAL_CACHE_HACK[task_hash]
            result = task_reference.revoke().get()
        except:
            pass

        return result

    def get_result(self, task_hash=None):
        '''Gets the result of a cached task and returns it'''

        #cache = get_cache('huey_tasks')
        #task_reference = cache.get(task_hash or self.task)

        result = None
        try:
            task_reference = TERRIBLE_GLOBAL_CACHE_HACK[task_hash or self.task]
            result = task_reference.get()
        except:
            pass

        return result
