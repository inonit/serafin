from __future__ import unicode_literals

from django import forms
from django.core.urlresolvers import reverse
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from system.models import Variable
import json


class PlumbingWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        context = {
            'value': value,
            'vars': json.dumps(list(Variable.objects.values_list('name', flat=True))),
            'admin_url': reverse('admin:index'),
            'node_api': reverse('api_node'),
            'reserved_vars': json.dumps(settings.RESERVED_VARIABLES)
        }
        html = render_to_string('admin/plumbing_widget.html', context)
        return mark_safe(html)

    class Media:
        css = {
            'all': (
                'plumbing/css/plumbing.css',
                'css/autocomplete.css',
                'css/expression-widget.css'
            )
        }
        js = (
            'lib/angular/angular.min.js',
            #'plumbing/jquery/jquery.min.js',
            'lib/jqueryui/jquery-ui.min.js',
            'lib/jsplumb/dist/js/jquery.jsPlumb-1.7.5-min.js',
            'lib/lodash/lodash.min.js',
            'lib/ment.io/dist/mentio.min.js',
            'js/autocomplete.js',
            'js/expression.js',
            'plumbing/js/plumbing.js',
        )
