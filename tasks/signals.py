from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db.models import signals
from django.dispatch import receiver
from .models import Task
from system.models import Part
from tasks import email_users, test_task
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone


@receiver(signals.post_save, sender=Part)
def schedule_part(sender, **kwargs):

    part = kwargs['instance']

    if kwargs['created']:
        task = Task()
        task.sender = part
        task.time = part.start_time

        # task_ref = email_users.schedule(
        #     args=(queryset, subject, message, html_message),
        #     eta=timezone.localtime(task.time).replace(tzinfo=None),
        #     convert_utc=False
        # )
        task_ref = test_task.schedule(
            eta=timezone.localtime(task.time).replace(tzinfo=None),
            convert_utc=False
        )
        task.task = task_ref

        task.action = _('Send login link for %(part)s' % {'part': part})

        task.save()


@receiver(signals.post_save, sender=Part)
def reschedule_part(sender, **kwargs):

    part = kwargs['instance']

    if not kwargs['created']:
        try:
            part_type = ContentType.objects.get_for_model(part)
            task = Task.objects.get(content_type=part_type, object_id=part.id)
        except:
            schedule_part(sender, instance=part, created=True)
            return

        task.time = part.start_time

        task.revoke()
        # task_ref = email_users.schedule(
        #     args=(queryset, subject, message, html_message),
        #     eta=timezone.localtime(task.time).replace(tzinfo=None),
        #     convert_utc=False
        # )
        task_ref = test_task.schedule(
            eta=timezone.localtime(task.time).replace(tzinfo=None),
            convert_utc=False
        )
        task.task = task_ref

        task.save()


@receiver(signals.pre_delete, sender=Part)
def revoke_part(sender, **kwargs):

    part = kwargs['instance']

    try:
        part_type = ContentType.objects.get_for_model(part)
        task = Task.objects.get(content_type=part_type, object_id=part.id)
    except:
        return

    task.revoke()
    task.delete()


@receiver(signals.pre_delete, sender=Task)
def revoke_task(sender, **kwargs):
    task = kwargs['instance']
    task.revoke()
