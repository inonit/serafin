from __future__ import unicode_literals

import time

from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from django.utils import timezone
from huey.contrib.djhuey import db_task
from system.engine import Engine
from tasker.models import Task


@db_task()
def transition(session_id, node_id, user_id, stack=None):
    '''A task to schedule an Engine transition'''

    context = {
        'session': session_id,
        'node': node_id,
        'stack': stack or []
    }

    engine = Engine(user_id=user_id, context=context)

    if not engine.user.is_active:
        return _('Inactive user, no action taken')

    node = engine.transition(node_id)

    message = _('%(session)s transitioned to node %(node)s') % {
        'session': engine.session.title,
        'node': getattr(node, 'name', node_id)
    }

    return message


@db_task()
def init_session(session_id, user_id, push=False):
    '''Initialize a given session from start and traverse on behalf of user'''

    context = {
        'session': session_id,
        'node': 0,
    }

    if not push:
        context['stack'] = []

    engine = Engine(user_id=user_id, context=context, push=push)
    original_session = engine.session

    if not engine.user.is_active:
        return _('Inactive user, no action taken')

    engine.run()

    if engine.session.trigger_login:
        engine.user.send_login_link()
        message = _('Session initialized and login e-mail sent')
    else:
        message = _('Session initialized')

    if original_session.scheduled and original_session.end_time_delta > 0:
        useraccess = engine.user.get_first_program_user_access(original_session.program)
        if original_session.get_end_time(useraccess.start_time, useraccess.time_factor) > \
                original_session.get_next_time(useraccess.start_time, useraccess.time_factor):

            next_time = original_session.get_next_time(useraccess.start_time, useraccess.time_factor)
            Task.objects.create_task(
                sender=original_session,
                domain='init',
                time=next_time,
                task=init_session,
                args=(session_id, user_id),
                action=_('Initialize session recurrent'),
                subject=engine.user
            )

    return message
