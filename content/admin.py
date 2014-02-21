from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib import admin
from django.db import models
from content.models import Text, Form, Image, Video, Audio, File
from suit.widgets import AutosizedTextarea


class TextAdmin(admin.ModelAdmin):
    model = Text
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }

class FormAdmin(admin.ModelAdmin):
    model = Form

class ImageAdmin(admin.ModelAdmin):
    model = Image
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }

class VideoAdmin(admin.ModelAdmin):
    model = Video
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }

class AudioAdmin(admin.ModelAdmin):
    model = Audio
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }

class FileAdmin(admin.ModelAdmin):
    model = File


admin.site.register(Text, TextAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(File, FileAdmin)
