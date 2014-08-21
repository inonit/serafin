from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth import get_user_model
from huey.djhuey import db_task
from system.engine import Engine


@db_task()
def transition(user_id, node_id):
    '''A task to schedule an Engine transition'''

    engine = Engine(user_id)
    engine.transition(node_id)


@db_task()
def init_session(session_id, user_id):
    '''Initialize a given session from start and traverse on behalf of user'''

    init = {
        'current_session': session_id,
        'current_page': 0,
    }

    engine = Engine(user_id, init)
    engine.run()
    engine.user.send_login_link()

    message = _('Session initialized and e-mail sent to user %i') % user_id

    return message
