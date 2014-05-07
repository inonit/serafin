from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from huey.djhuey import db_task
from system.engine import Engine
from users.models import User


@db_task()
def traverse(user, node_id):
    '''A task to schedule an Engine transition'''

    engine = Engine(user)
    engine.run()


@db_task()
def init_part(part):
    '''Initialize a given part from start and traverse on behalf of user'''

    users = User.objects.filter(active=True)

    for user in users:

        engine = Engine(
            user, {
                'current_part': part.id,
                'current_node': 0,
            }
        )
        engine.run()

        user.send_email(subject, message, html_message)

    message = _('Part initialized and user e-mails sent' % locals())

    print message
    return message
