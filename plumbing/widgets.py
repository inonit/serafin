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
            'admin_page_new': reverse('admin:system_page_add'),
            'admin_page_add': reverse('admin:system_page_changelist'),
            'admin_email_new': reverse('admin:content_email_add'),
            'admin_email_add': reverse('admin:content_email_changelist'),
            'admin_sms_new': reverse('admin:content_sms_add'),
            'admin_sms_add': reverse('admin:content_sms_changelist'),
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
            'plumbing/jsplumb/jquery.jsPlumb-1.5.5.js',
            'plumbing/js/plumbing.js',
        )
