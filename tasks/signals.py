from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db.models import signals
from django.dispatch import receiver
from models import Task
from system.models import Part


@receiver(signals.post_save, sender=Part)
def schedule_part(sender, instance, created, **kwargs):
    if created:
        task = Task()
        task.sender = instance
        task.time = instance.start_time
        # add task
        task.save()

        # trigger task to send out this Part's login e-mail

        if instance.end_time:
            task = Task()
            task.sender = instance
            task.time = instance.end_time
            # add task
            task.save()

            # trigger task to send out this Part's login e-mail


@receiver(signals.post_save, sender=Part)
def reschedule_part(sender, instance, created, **kwargs):
    if not created:
        try:
            task = Task.objects.get(sender=instance)
            # reschedule task to send out this Part's login e-mail
            task.save()
        except:
            schedule_part(sender, instance, True, **kwargs)


@receiver(signals.pre_delete, sender=Part)
def revoke_part(sender, instance, created, **kwargs):
    try:
        task = Task.objects.get(sender=instance)
        # revoke task to send out this Part's login e-mail
        task.delete()
    except:
        pass


@receiver(signals.pre_delete, sender=Task)
def revoke_task(sender, instance, created, **kwargs):
    task = instance
    # revoke task to send out this Part's login e-mail

