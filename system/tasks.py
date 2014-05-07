from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from huey.djhuey import db_task
from system.engine import Engine
from django.contrib.auth import get_user_model


@db_task()
def transition(user, node_id):
    '''A task to schedule an Engine transition'''

    engine = Engine(user)
    engine.transition(node_id)


@db_task()
def init_part(part):
    '''Initialize a given part from start and traverse on behalf of user'''

    users = get_user_model().objects.filter(is_active=True)

    for user in users:

        engine = Engine(
            user, {
                'current_part': part.id,
                'current_node': 0,
            }
        )
        engine.run()

        user.send_login_link()

    message = _('Part initialized and user e-mails sent' % locals())

    return message
