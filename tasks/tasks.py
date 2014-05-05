from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from huey.djhuey import task


@task()
def test_task():
    message = 'Hello Huey!'

    print message
    return message


@task()
def email_users(queryset, subject, message, html_message):
    counter = 0

    for user in queryset:
        ok = user.send_email(subject, message, html_message)

        if ok:
            counter += 1

    message = _('%(counter)i e-mails with subject "%(subject)s" sent' % locals())

    print message
    return message
