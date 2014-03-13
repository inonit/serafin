from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from huey.djhuey import task


@task
def email_users(queryset, subject, message, html_message):
    counter = 0

    for user in queryset:
        ok = user.send_email(subject, message, html_message)

        if ok:
            counter += 1

    return _('%i e-mails sent' % counter)
