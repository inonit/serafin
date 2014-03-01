from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from fluent_contents.extensions import plugin_pool, ContentPlugin
from content.models import Text, Form, Image, Video, Audio, File
from django.db import models
from suit.widgets import AutosizedTextarea


@plugin_pool.register
class TextPlugin(ContentPlugin):
    model = Text
    render_template = 'content/text.html'
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }


@plugin_pool.register
class FormPlugin(ContentPlugin):
    model = Form
    render_template = 'content/form.html'


@plugin_pool.register
class ImagePlugin(ContentPlugin):
    model = Image
    render_template = 'content/image.html'
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }


@plugin_pool.register
class VideoPlugin(ContentPlugin):
    model = Video
    render_template = 'content/video.html'
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }


@plugin_pool.register
class AudioPlugin(ContentPlugin):
    model = Audio
    render_template = 'content/audio.html'
    formfield_overrides = {
        models.TextField: {
            'widget': AutosizedTextarea(attrs={'rows': 5, 'class': 'input-xlarge'}),
        }
    }


@plugin_pool.register
class FilePlugin(ContentPlugin):
    model = File
    render_template = 'content/file.html'
