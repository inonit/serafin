from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

import re

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases
from .models import Variable, ProgramUserAccess, Session, Content, Page
from tasker.models import Task
from system.tasks import init_session


def disable_for_loaddata(signal_handler):
    '''Turn of signal handling for loaddata'''

    def _disable_for_loaddata(*args, **kwargs):
        if kwargs.get('raw'):
            return
        signal_handler(*args, **kwargs)

    return _disable_for_loaddata


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


def execute_schedule_sessions(sender, **kwargs):

    useraccess = kwargs['instance']

    if not useraccess.user.is_active:
        return

    session_type = ContentType.objects.get_for_model(Session)
    for session in useraccess.program.session_set.all():

        Task.objects.filter(
            content_type=session_type,
            object_id=session.id,
            subject=useraccess.user
        ).delete()

        if not useraccess.user.is_active:
            continue

        if session.scheduled:

            start_time = session.get_start_time(
                useraccess.start_time,
                useraccess.time_factor
            )

            Task.objects.create_task(
                sender=session,
                domain='init',
                time=start_time,
                task=init_session,
                args=(session.id, useraccess.user.id),
                action=_('Initialize session'),
                subject=useraccess.user
            )


@receiver(signals.post_save, sender=ProgramUserAccess)
@disable_for_loaddata
def schedule_sessions(sender, **kwargs):
    transaction.on_commit(lambda: execute_schedule_sessions(sender, **kwargs))


@receiver(signals.pre_save, sender=Session)
@disable_for_loaddata
def session_pre_save(sender, **kwargs):

    session = kwargs['instance']

    nodes = session.data.get('nodes', [])
    for node in nodes:
        ref_id = node.get('ref_id')
        node_type = node.get('type')

        if node_type in ['page', 'email', 'sms', 'session']:

            # Temp. dirty fix for occational empty ref_ids
            if not ref_id or ref_id == '0':
                ref_url = node.get('ref_url', '')
                try:
                    node['ref_id'] = re.findall(r'\d+', ref_url)[0]
                except:
                    pass

            # Update title of content
            if node_type in ['page', 'email', 'sms']:
                try:
                    node['title'] = Content.objects.get(id=node['ref_id']).title
                except:
                    pass
            # Update title of sessions
            elif node_type == 'session':
                try:
                    node['title'] = Session.objects.get(id=node['ref_id']).title
                except:
                    pass

    session.data['nodes'] = nodes

    first_useraccess = session.program.programuseraccess_set.order_by('start_time').first()
    if first_useraccess and session.scheduled:

        session.start_time = session.get_start_time(
            first_useraccess.start_time,
            first_useraccess.time_factor
        )


@receiver(signals.post_save, sender=Session)
def add_content_relations(sender, **kwargs):

    session = kwargs['instance']

    session.content.clear()
    ids = [
        node['ref_id'] for node in session.data['nodes']
        if node['type'] in ['page', 'email', 'sms']
    ]
    ids = list(set(ids))
    ids = Content.objects.filter(id__in=ids).values_list('id', flat=True)
    session.content.add(*ids)


@receiver(signals.post_save, sender=Session)
@disable_for_loaddata
def schedule_session(sender, **kwargs):

    session = kwargs['instance']

    if kwargs['created'] and session.scheduled:
        for useraccess in session.program.programuseraccess_set.all():

            if not useraccess.user.is_active:
                continue

            start_time = session.get_start_time(
                useraccess.start_time,
                useraccess.time_factor
            )

            if start_time > timezone.localtime(timezone.now()):
                Task.objects.create_task(
                    sender=session,
                    domain='init',
                    time=start_time,
                    task=init_session,
                    args=(session.id, useraccess.user.id),
                    action=_('Initialize session'),
                    subject=useraccess.user
                )
            elif session.get_end_time(useraccess.start_time, useraccess.time_factor) > \
                    session.get_next_time(useraccess.start_time, useraccess.time_factor):
                next_time = session.get_next_time(useraccess.start_time, useraccess.time_factor)
                Task.objects.create_task(
                    sender=session,
                    domain='init',
                    time=next_time,
                    task=init_session,
                    args=(session.id, useraccess.user.id),
                    action=_('Initialize session recurrent'),
                    subject=useraccess.user
                )


@receiver(signals.post_save, sender=Session)
def reschedule_session(sender, **kwargs):

    session = kwargs['instance']

    if not kwargs['created']:
        session_type = ContentType.objects.get_for_model(Session)
        for useraccess in session.program.programuseraccess_set.all():

            Task.objects.filter(
                content_type=session_type,
                object_id=session.id,
                subject=useraccess.user,
                time__gt=timezone.localtime(timezone.now())
            ).delete()

            if not useraccess.user.is_active:
                continue

            start_time = session.get_start_time(
                useraccess.start_time,
                useraccess.time_factor
            )
            if session.scheduled:
                if start_time > timezone.localtime(timezone.now()):
                    Task.objects.create_task(
                        sender=session,
                        domain='init',
                        time=start_time,
                        task=init_session,
                        args=(session.id, useraccess.user.id),
                        action=_('Initialize session'),
                        subject=useraccess.user
                    )
                elif session.get_end_time(useraccess.start_time, useraccess.time_factor) > \
                        session.get_next_time(useraccess.start_time, useraccess.time_factor):
                    next_time = session.get_next_time(useraccess.start_time, useraccess.time_factor)
                    Task.objects.create_task(
                        sender=session,
                        domain='init',
                        time=next_time,
                        task=init_session,
                        args=(session.id, useraccess.user.id),
                        action=_('Initialize session recurrent'),
                        subject=useraccess.user
                    )


@receiver(signals.pre_delete, sender=Session)
def revoke_session(sender, **kwargs):

    session = kwargs['instance']

    session_type = ContentType.objects.get_for_model(Session)

    Task.objects.filter(
        content_type=session_type,
        object_id=session.id
    ).delete()


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


@receiver(signals.post_save)
def content_post_save(sender, **kwargs):

    content_types = ['Page', 'Email', 'SMS']
    node_types = [t.lower() for t in content_types]

    if sender.__name__ in content_types:

        content = kwargs['instance']

        # Update title in all sessions
        for session in Session.objects.all():

            data = session.data
            nodes = data.get('nodes', [])
            for node in nodes:
                try:
                    if node['type'] in node_types and node['ref_id'] == content.id:
                        node['title'] = content.title

                        # ...gently
                        Session.objects.filter(id=session.id).update(data=data)
                except:
                    pass

        # Replace images with thumbnails
        data = content.data
        aliases.populate_from_settings()


        for pagelet in data:

            if pagelet.get('content_type') == 'image':

                url = pagelet['content']['url'].replace(settings.MEDIA_URL, '')

                if url:

                    try:
                        options = aliases.get('medium')
                        thumbnail = get_thumbnailer(url).get_thumbnail(options).url
                    except:
                        thumbnail = None

                    if thumbnail:
                        pagelet['content']['thumbnail'] = thumbnail
                        Content.objects.filter(id=content.id).update(data=data)

            if pagelet.get('content_type') == 'toggle':
                if not 'img_content' in pagelet:
                    pagelet['img_content'] = {
                        'url': ''
                    }

                url = pagelet['img_content']['url'].replace(settings.MEDIA_URL, '')

                if url:

                    try:
                        options = aliases.get('small')
                        thumbnail = get_thumbnailer(url).get_thumbnail(options).url
                    except:
                        thumbnail = None

                    if thumbnail:
                        pagelet['img_content']['thumbnail'] = thumbnail
                        Content.objects.filter(id=content.id).update(data=data)
