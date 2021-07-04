# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from builtins import object
from django import forms
from django.conf import settings
from django.contrib.admin.sites import site
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from filer.fields.file import AdminFileWidget
import re
import json


class DummyForeignObjectRel(object):
    class DummyRelatedField(object):
        name = ''

    def __init__(self, *args, **kwargs):
        self.limit_choices_to = {}

    def get_related_field(self):
        return self.DummyRelatedField()

    @property
    def model(self):
        return None


class ContentWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        file_widget = AdminFileWidget(DummyForeignObjectRel(), site)
        file_widget = file_widget.render('file', None, {'id': 'id_file'})
        file_widget = re.sub(r'<script.*?>.*?</script>', r'', file_widget, flags=re.DOTALL)

        context = {
            'value': value,
            'file_widget': file_widget,
            'filer_api': reverse('content_api'),
            'reserved_vars': json.dumps(settings.RESERVED_VARIABLES)
        }

        html = render_to_string('admin/content_widget.html', context)
        return mark_safe(html)

    class Media(object):
        css = {
            'all': (
                'filer/css/admin_filer.css',
                'css/autocomplete.css',
                'css/expression-widget.css',
                'css/fonts.css',
                'css/content.css'
            )
        }
        js = (
            'admin/js/admin/RelatedObjectLookups.js',
            'filer/js/libs/dropzone.min.js',
            'filer/js/addons/dropzone.init.js',
            'filer/js/addons/popup_handling.js',
            'filer/js/addons/widget.js',
            'lib/angular/angular.min.js',
            'lib/lodash/lodash.min.js',
            'lib/ment.io/dist/mentio.min.js',
            'lib/marked/marked.min.js',
            'lib/angular-sanitize/angular-sanitize.min.js',
            'lib/angular-ui-tinymce/dist/tinymce.min.js',
            'js/autocomplete.js',
            'js/expression.js',
            'js/content.js',
        )


class TextContentWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        context = {
            'value': value,
        }

        html = render_to_string('admin/text_content_widget.html', context)
        return mark_safe(html)

    class Media(object):
        css = {
            'all': (
                'css/content.css',
            )
        }
        js = (
            'lib/angular/angular.min.js',
            'lib/lodash/lodash.min.js',
            'lib/ment.io/dist/mentio.min.js',
            'lib/marked/marked.min.js',
            'js/autocomplete.js',
            'js/expression.js',
            'js/content.js',
        )


class SMSContentWidget(forms.Widget):

    def render(self, name, value, attrs=None, renderer=None):
        # verify is_whatsapp flag
        j = json.loads(value)
        if len(j) == 1:
            j.append({'content_type': 'is_whatsapp', 'content': False})
            value = json.dumps(j)

        context = {
            'value': value,
        }

        html = render_to_string('admin/sms_content_widget.html', context)
        return mark_safe(html)

    class Media(object):
        css = {
            'all': (
                'css/content.css',
            )
        }
        js = (
            'lib/angular/angular.min.js',
            'lib/lodash/lodash.min.js',
            'lib/ment.io/dist/mentio.min.js',
            'js/autocomplete.js',
            'js/expression.js',
            'js/content.js',
        )
