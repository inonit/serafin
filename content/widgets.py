from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib.admin.sites import site
from filer.fields.file import AdminFileWidget
from filer import settings as filer_settings
import re


class DummyForeignObjectRel:
    class DummyRelatedField:
        name = None

    def __init__(self, *args, **kwargs):
        self.limit_choices_to = {}

    def get_related_field(self):
        return self.DummyRelatedField()


class ContentWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        file_widget = AdminFileWidget(DummyForeignObjectRel(), site).render('file', None, {'id': 'id_file'})
        file_widget = re.sub(r'<script.*?>.*?</script>', r'', file_widget, flags=re.DOTALL)

        context = {
            'value': value,
            'file_widget': file_widget,
        }

        html = render_to_string('admin/content_widget.html', context)
        return mark_safe(html)

    class Media:
        css = {
            'all': (
                'content/content/css/content.css',
            )
        }
        js = (
            filer_settings.FILER_STATICMEDIA_PREFIX + 'js/popup_handling.js',
            'content/content/angular/angular.min.js',
            'content/js/marked.js',
            'content/js/content.js',
        )
