from __future__ import unicode_literals

from builtins import object
from import_export import resources
from events.models import Event


class EventResource(resources.ModelResource):
    """Import-Export resource for Event model"""
    class Meta(object):
        model = Event
