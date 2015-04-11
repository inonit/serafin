from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.db.models import signals
from django.dispatch import receiver
from django.utils import timezone

from easy_thumbnails.files import get_thumbnailer
from easy_thumbnails.alias import aliases
from .models import Variable, ProgramUserAccess, Session, Content, Page
from tasker.models import Task
from system.tasks import init_session


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


@receiver(signals.post_save, sender=Session)
def reschedule_session(sender, **kwargs):

    session = kwargs['instance']

    if not kwargs['created']:
        session_type = ContentType.objects.get_for_model(Session)
        for useraccess in session.program.programuseraccess_set.all():
            Task.objects.filter(
                content_type=session_type,
                object_id=session.id,
                subject=useraccess.user
            ).delete()

            start_time = session.get_start_time(
                useraccess.start_time,
                useraccess.time_factor
            )
            if start_time > timezone.localtime(timezone.now()) and session.scheduled:
                Task.objects.create_task(
                    sender=session,
                    domain='init',
                    time=start_time,
                    task=init_session,
                    args=(session.id, useraccess.user.id),
                    action=_('Initialize session'),
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


@receiver(signals.pre_save, sender=Session)
def session_pre_save(sender, **kwargs):

    session = kwargs['instance']

    nodes = session.data.get('nodes', [])
    for node in nodes:
        ref_id = node.get('ref_id')
        node_type = node.get('type')

        if node_type in ['page', 'email', 'sms']:

            # Temp. dirty fix for occational empty ref_ids
            if not ref_id:
                ref_url = node.get('ref_url')
                try:
                    node['ref_id'] = re.findall(r'\d+', ref_url)[0]
                except:
                    pass

            # Update title of content
            try:
                node['title'] = Content.objects.get(id=node['ref_id']).title
            except:
                pass

    session.data['nodes'] = nodes


@receiver(signals.post_save)
def content_post_save(sender, **kwargs):

    content_types = ['Page', 'Email', 'SMS']
    if sender.__name__ in content_types:

        content = kwargs['instance']

        # Update title in all sessions
        for session in Session.objects.all():

            data = session.data
            nodes = data.get('nodes', [])
            for node in nodes:
                try:
                    if int(node['ref_id']) == content.id:
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

                    options = aliases.get('medium')
                    thumbnail = get_thumbnailer(url).get_thumbnail(options).url

                    if thumbnail:

                        pagelet['content']['thumbnail'] = thumbnail
                        Content.objects.filter(id=content.id).update(data=data)

            if pagelet.get('content_type') == 'toggle':
                if not pagelet['img_content']:
                    pagelet['img_content'] = {
                        'url': ''
                    }

                url = pagelet['img_content']['url'].replace(settings.MEDIA_URL, '')

                if url:

                    options = aliases.get('small')
                    thumbnail = get_thumbnailer(url).get_thumbnail(options).url

                    if thumbnail:

                        pagelet['img_content']['thumbnail'] = thumbnail
                        Content.objects.filter(id=content.id).update(data=data)
