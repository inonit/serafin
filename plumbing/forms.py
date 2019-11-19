from __future__ import unicode_literals
from __future__ import absolute_import

from django import forms
from .widgets import PlumbingWidget


class PlumbingField(forms.Field):
    widget = PlumbingWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('required', False)
        super(PlumbingField, self).__init__(*args, **kwargs)

    def bound_data(self, data, initial):
        return initial

    def _has_changed(self, initial, data):
        return False
