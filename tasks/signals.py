from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db.models import signals
from django.dispatch import receiver
from models import Task
from system.models import Part
from tasks import email_users


@receiver(signals.post_save, sender=Part)
def schedule_part(sender, instance, created, **kwargs):
    if created:
        task = Task()
        task.sender = instance
        task.time = instance.start_time

        task.task = email_users.schedule(
            args=(queryset, subject, message, html_message), eta=instance.start_time
        )

        task.save()


@receiver(signals.post_save, sender=Part)
def reschedule_part(sender, instance, created, **kwargs):
    if not created:
        try:
            task = Task.objects.get(sender=instance)
        except:
            schedule_part(sender, instance, True, **kwargs)
            return

        task.time = instance.start_time

        task.task.revoke()
        task.task = email_users.schedule(
            args=(queryset, subject, message, html_message), eta=instance.start_time
        )

        task.save()


@receiver(signals.pre_delete, sender=Part)
def revoke_part(sender, instance, created, **kwargs):
    try:
        task = Task.objects.get(sender=instance)
    except:
        return

    task.task.revoke()
    task.delete()


@receiver(signals.pre_delete, sender=Task)
def revoke_task(sender, instance, created, **kwargs):
    task = instance
    task.task.revoke()

