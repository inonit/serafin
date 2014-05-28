from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from .models import Session
from system.tasks import init_session
from tasker.models import Task


@receiver(signals.post_save, sender=Session)
def schedule_session(sender, **kwargs):

    session = kwargs['instance']

    if kwargs['created']:
        for useraccess in session.program.programuseraccess_set.all():
            Task.objects.create_task(
                sender=session,
                time=session.get_start_time(useraccess.start_time, useraccess.time_factor),
                task=init_session,
                args=(session, useraccess.user),
                action=_('Send login link and start traversal for %(useraccess)s') % locals()
            )


@receiver(signals.post_save, sender=Session)
def reschedule_session(sender, **kwargs):

    session = kwargs['instance']

    if not kwargs['created']:
        for useraccess in session.program.programuseraccess_set.all():
            try:
                session_type = ContentType.objects.get_for_model(session)
                task = Task.objects.get(content_type=session_type, object_id=session.id)
            except:
                schedule_session(sender, instance=session, created=True)
                return

            task.reschedule(
                task=init_session,
                args=(session, useraccess.user),
                time=session.get_start_time(useraccess.start_time, useraccess.time_factor)
            )
            task.save()


@receiver(signals.pre_delete, sender=Session)
def revoke_session(sender, **kwargs):

    session = kwargs['instance']

    try:
        session_type = ContentType.objects.get_for_model(session)
        task = Task.objects.get(content_type=session_type, object_id=session.id)
    except:
        return

    task.delete()
