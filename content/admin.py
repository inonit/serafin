from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django import forms
from django.contrib import admin
from content.models import Text, Form, Image, Video, Audio, File


class TextAdmin(admin.ModelAdmin):
    model = Text

class FormAdmin(admin.ModelAdmin):
    model = Form

class ImageAdmin(admin.ModelAdmin):
    model = Image

class VideoAdmin(admin.ModelAdmin):
    model = Video

class AudioAdmin(admin.ModelAdmin):
    model = Audio

class FileAdmin(admin.ModelAdmin):
    model = File


admin.site.register(Text, TextAdmin)
admin.site.register(Form, FormAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(File, FileAdmin)
