from __future__ import unicode_literals

from builtins import object
from django import forms
from django.urls import reverse
from django.conf import settings
from django.contrib.admin.sites import site
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from system.models import Variable
from filer.fields.file import AdminFileWidget
from content.widgets import DummyForeignObjectRel
import re
import json


class PlumbingWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        file_widget = AdminFileWidget(DummyForeignObjectRel(), site)
        file_widget = file_widget.render('file', None, {'id': 'id_file'})
        file_widget = re.sub(r'<script.*?>.*?</script>', r'', file_widget, flags=re.DOTALL)

        context = {
            'value': value,
            'file_widget': file_widget,
            'filer_api': reverse('content_api'),
            'vars': json.dumps(list(Variable.objects.values_list('name', flat=True))),
            'admin_url': reverse('admin:index'),
            'node_api': reverse('api_node'),
            'reserved_vars': json.dumps(settings.RESERVED_VARIABLES)
        }
        html = render_to_string('admin/plumbing_widget.html', context)
        return mark_safe(html)

    class Media(object):
        css = {
            'all': (
                '//stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
                'filer/css/admin_filer.css',
                'css/plumbing.css',
                'css/autocomplete.css',
                'css/expression-widget.css'
            )
        }
        js = (
            'lib/angular/angular.min.js',
            'lib/jqueryui/jquery-ui.min.js',
            'lib/jsplumb/dist/js/jsPlumb-1.7.10-min.js',
            'lib/lodash/lodash.min.js',
            'lib/ment.io/dist/mentio.min.js',
            'filer/js/libs/dropzone.min.js',
            'filer/js/addons/dropzone.init.js',
            'filer/js/addons/popup_handling.js',
            'filer/js/addons/widget.js',
            'js/autocomplete.js',
            'js/expression.js',
            'js/plumbing.js',
        )
