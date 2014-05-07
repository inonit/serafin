from __future__ import unicode_literals

from django.db.models import signals
from django.dispatch import receiver
from tasker.models import Task


@receiver(signals.pre_delete, sender=Task)
def revoke_task(sender, **kwargs):
    task = kwargs['instance']
    task.revoke()
