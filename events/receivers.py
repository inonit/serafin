from django.dispatch import receiver
from signals import log_event
from models import Event

@receiver(log_event)
def handle_log_event(sender, **kwargs):
    domain = kwargs.get("domain")
    actor = kwargs.get("actor")
    variable = kwargs.get("variable")
    pre_value = kwargs.get("pre_value")
    post_value = kwargs.get("post_value")
    event = Event(domain=domain, actor=actor, variable=variable, pre_value=pre_value, post_value=post_value)
    event.save()
