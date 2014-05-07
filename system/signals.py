from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from .models import Part
from system.tasks import init_part
from tasker.models import Task


@receiver(signals.post_save, sender=Part)
def schedule_part(sender, **kwargs):

    part = kwargs['instance']

    if kwargs['created']:
        Task.objects.create_task(
            sender=part,
            time=part.start_time,
            task=init_part,
            args=(part),
            action=_('Send login link and start traversal for all users')
        )


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

        task.reschedule(
            task=init_part,
            args=(part),
            time=part.start_time
        )
        task.save()


@receiver(signals.pre_delete, sender=Part)
def revoke_part(sender, **kwargs):

    part = kwargs['instance']

    try:
        part_type = ContentType.objects.get_for_model(part)
        task = Task.objects.get(content_type=part_type, object_id=part.id)
    except:
        return

    task.delete()
