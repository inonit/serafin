from django import forms
from django.utils.safestring import mark_safe
import os

class ContentWidget(forms.Widget):

    def render(self, name, value, attrs=None):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'templates/content_widget.html')

        with open (filename, 'r') as template:
            html = template.read()

        html += '<script>var initData = %s;</script>' % value

        return mark_safe(html)

    class Media:
        css = {
            'all': (
                'content/content/css/content.css',
            )
        }
        js = (
            'content/content/angular/angular.min.js',
            'content/js/marked.js',
            'content/js/content.js',
        )
