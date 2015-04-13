from django.contrib.auth import get_user_model
from django.dispatch import receiver, Signal

from models import Event


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

    event = Event(domain=domain, actor=actor, variable=variable, pre_value=pre_value, post_value=post_value)
    event.save()
