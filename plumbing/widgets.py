from __future__ import unicode_literals

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.urlresolvers import reverse


class PlumbingWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        context = {
            'value': value,
            'admin_page_new': reverse('admin:system_page_add'),
            'admin_page_add': reverse('admin:system_page_changelist'),
            'page_api': reverse('api_page'),
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
