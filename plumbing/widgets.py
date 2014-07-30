from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse
from system.models import Variable
import json


class PlumbingWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        context = {
            'value': value,
            'vars': json.dumps(list(Variable.objects.values_list('name', flat=True))),
            'admin_url': reverse('admin:index'),
            'node_api': reverse('api_node'),
        }
        html = render_to_string('admin/plumbing_widget.html', context)
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
            'plumbing/jsplumb/jquery.jsPlumb-1.6.2-min.js',
            'plumbing/js/plumbing.js?v=1.05',
        )
