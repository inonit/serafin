from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver

from .models import Variable, ProgramUserAccess, Session, Content, Page
from tasker.models import Task


@receiver(signals.pre_save, sender=Variable)
def randomize_variable_once(sender, **kwargs):
    variable = kwargs['instance']
    original = None
    changed = False
    created = False

    try:
        original = Variable.objects.get(id=variable.id)
    except Variable.DoesNotExist:
        created = True

    if not created:
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

    if variable.random_type and variable.randomize_once and (created or changed):
        for user in get_user_model().objects.all():
            user.data[variable.name] = variable.get_value()
            user.save()


@receiver(signals.post_save, sender=Session)
def schedule_session(sender, **kwargs):

    session = kwargs['instance']

    if kwargs['created'] and session.scheduled:
        for useraccess in session.program.programuseraccess_set.all():
            Task.objects.create_task(
                sender=session,
                time=session.get_start_time(useraccess.start_time, useraccess.time_factor),
                task=init_session,
                args=(session.id, useraccess.user.id),
                action=_('Send login link and start traversal'),
                subject=useraccess.user
            )


@receiver(signals.post_save, sender=Session)
def reschedule_session(sender, **kwargs):

    session = kwargs['instance']

    if not kwargs['created'] and session.scheduled:
        session_type = ContentType.objects.get_for_model(Session)
        for useraccess in session.program.programuseraccess_set.all():
            try:
                task = Task.objects.get(
                    content_type=session_type,
                    object_id=session.id,
                    subject=useraccess.user
                )
            except Task.DoesNotExist:
                Task.objects.create_task(
                    sender=session,
                    time=session.get_start_time(useraccess.start_time, useraccess.time_factor),
                    task=init_session,
                    args=(session.id, useraccess.user.id),
                    action=_('Send login link and start traversal'),
                    subject=useraccess.user
                )
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

    if session.scheduled:
        session_type = ContentType.objects.get_for_model(Session)
        Task.objects.filter(content_type=session_type, object_id=session.id).delete()


@receiver(signals.pre_delete, sender=ProgramUserAccess)
def revoke_tasks(sender, **kwargs):

    useraccess = kwargs['instance']

    session_type = ContentType.objects.get_for_model(Session)
    for session in useraccess.program.session_set.all():
        Task.objects.filter(
            content_type=session_type,
            object_id=session.id,
            subject=useraccess.user
        ).delete()


@receiver(signals.pre_save, sender=Session)
def session_pre_save(sender, instance, *args, **kwargs):

    # Temp. dirty fix for occational empty ref_ids
    for node in instance.data.get('nodes', []):
        ref_id = node.get('ref_id')
        node_type = node.get('type')
        if ref_id == '' and node_type in ['page', 'email', 'sms']:

            ref_url = node.get('ref_url')
            try:
                node['ref_id'] = re.findall('\d+', ref_url)[0]

                # Update title of all content
                content = Content.objects.filter(id=node['ref_id'])
                node['title'] = content.title
            except:
                pass

@receiver(signals.post_save, sender=Content)
def content_post_save(sender, instance, *args, **kwargs):

    # Update title in all sessions
    for session in Session.objects.all():
        nodes = session.data.get('nodes', [])
        for node in nodes:
            try:
                if int(node.get('ref_id')) == instance.id:
                    node['title'] = instance.title
                    session.save()
            except:
                pass
