from __future__ import unicode_literals

from django.db.models import signals
from django.dispatch import receiver
from .models import User

@receiver(signals.pre_delete, sender=User)
def delete_mirror(sender, **kwargs):
    kwargs['instance']._delete_mirror()
