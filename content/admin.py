from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.db import models
from django.contrib import admin
from suit.widgets import LinkedSelect, AutosizedTextarea
from jsonfield import JSONField

from content.models import Email, SMS
from content.widgets import TextContentWidget


class ContentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ContentForm, self).__init__(*args, **kwargs)
        self.fields['data'].help_text = ''


class ContentAdmin(admin.ModelAdmin):
    list_display = ['title', 'part', 'note_excerpt', 'page_excerpt']
    search_fields = ['title', 'part', 'admin_note', 'data']

    fields = ['title', 'part', 'admin_note', 'data']
    readonly_fields = ['part']
    formfield_overrides = {
        models.TextField: {'widget': AutosizedTextarea(attrs={'rows': 3, 'class': 'input-xlarge'})},
        models.ForeignKey: {'widget': LinkedSelect},
        JSONField: {'widget': TextContentWidget}
    }

    def page_excerpt(self, obj):
        display = _('No content')
        if len(obj.data) > 0:
            if obj.data[0]['content_type'] == 'text':
                display = obj.data[0]['content']['text'][:100] + '...'
            else:
                display = '(%s data)' % obj.data[0]['content_type']
        return display

    page_excerpt.short_description = _('Page excerpt')

    def note_excerpt(self, obj):
        return obj.admin_note[:100] + '...'

    note_excerpt.short_description = _('Admin note excerpt')


class EmailForm(ContentForm):
    class Meta:
        model = Email


class EmailAdmin(ContentAdmin):
    form = EmailForm


class SMSForm(ContentForm):
    class Meta:
        model = SMS


class SMSAdmin(ContentAdmin):
    form = SMSForm


admin.site.register(Email, EmailAdmin)
admin.site.register(SMS, SMSAdmin)
