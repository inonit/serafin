from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db.models import signals
from django.dispatch import receiver
from models import Event

#@receiver(some_signal)
#def react_to_signal(sender, **kwargs):
#    pass
