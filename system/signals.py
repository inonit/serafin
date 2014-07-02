from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from .models import Variable, Session
from system.tasks import init_session
from tasker.models import Task


@receiver(signals.post_save, sender=Variable)
def randomize_variable_once(sender, **kwargs):
    variable = kwargs['instance']
    created = kwargs['created']
    changed = False

    if not created:
        original = Variable.objects.get(id=variable.id)
        for field in [
            'name',
            'value',
            'random_type',
            'randomize_once',
            'range_min',
            'range_max',
            'random_set']:
            if getattr(variable, field) != getattr(original, field):
                changed = True

    if (variable.random_type and variable.randomize_once) and (created or changed):
        for user in get_user_model().objects.all():
            user.data[variable.name] = variable.get_value()
            user.save()


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
