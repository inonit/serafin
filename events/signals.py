from __future__ import unicode_literals
from django.db.models.signals import post_save, pre_save

from django.dispatch import receiver
from events.models import Event


#@receiver(pre_save, sender=User)
def track_event(instance, sender, **kwargs):
    # ignore events apps
    # create log event entry
    from users.models import User

    if not isinstance(instance, Event):
        try:
            obj = sender.objects.get(id=instance.id)
            obj_fields = instance._meta.fields
            for field in obj_fields:
                pre_value = getattr(obj, field.name)
                post_value = getattr(instance, field.name)
                if pre_value != post_value:
                    Event.objects.create_event(
                        domain=sender.__name__,
                        actor=User.objects.get(id=1),
                        variable=field.name,
                        pre_value=pre_value,
                        post_value=post_value
                    )
        except sender.DoesNotExist:
            Event.objects.create_event(
                domain=sender.__name__,
                actor=User.objects.get(id=1),
                variable='created',
                pre_value='',
                post_value=''
            )




