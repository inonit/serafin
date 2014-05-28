from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from huey.djhuey import db_task
from system.engine import Engine


@db_task()
def transition(user, node_id):
    '''A task to schedule an Engine transition'''

    engine = Engine(user)
    engine.transition(node_id)


@db_task()
def init_session(session, group):
    '''Initialize a given session from start and traverse on behalf of user'''

    init = {
        'current_session': session.id,
        'current_node': 0,
    }

    for user in group.user_set.filter(is_active=True):

        engine = Engine(user, init)
        engine.run()

        user.send_login_link()

    message = _('Session initialized and user e-mails sent') % locals()

    return message
