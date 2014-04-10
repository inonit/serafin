from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class PlumbingWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        html = render_to_string('admin/plumbing_widget.html', { 'value': value })
        return mark_safe(html)

    class Media:
        css = {
            'all': (
                'plumbing/css/plumbing.css',
            )
        }
        js = (
            'plumbing/angular/angular.min.js',
            'plumbing/jquery/jquery.min.js',
            'plumbing/jqueryui/jquery-ui.min.js',
            'plumbing/jsplumb/jquery.jsPlumb-1.5.5-min.js',
            'plumbing/js/plumbing.js',
        )
