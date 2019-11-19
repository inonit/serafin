from __future__ import unicode_literals
from __future__ import absolute_import
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver, Signal

from .models import Event


log_event = Signal(providing_args=["domain", "actor", "variable", "pre_value", "post_value"])


@receiver(log_event)
def handle_log_event(sender, **kwargs):
    domain = kwargs.get("domain")
    actor = kwargs.get("actor")
    variable = kwargs.get("variable")
    pre_value = kwargs.get("pre_value")
    post_value = kwargs.get("post_value")

    if not isinstance(actor, get_user_model()):
        return

    event = Event(
        domain=domain,
        actor=actor,
        variable=variable,
        pre_value=pre_value,
        post_value=post_value
    )
    event.save()


@receiver(user_logged_in)
def handle_login(sender, user, request, **kwargs):

    summary = ''
    if getattr(settings, 'LOG_DEVICE_ON_LOGIN', False):
        device = _('Other')
        if request.user_agent.is_mobile:
            device = _('Mobile')
        elif request.user_agent.is_tablet:
            device = _('Tablet')
        elif request.user_agent.is_pc:
            device = _('PC')

        summary = '%s, %s %s %s' % (
            device,
            request.user_agent.device.family,
            request.user_agent.os.family,
            request.user_agent.os.version_string,
        )

    event = Event(
        domain='user',
        actor=user,
        variable='login',
        pre_value='',
        post_value=summary
    )
    event.save()
