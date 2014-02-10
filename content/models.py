from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from filer.fields.image import FilerImageField
from filer.fields.file import FilerFileField


class Content(models.Model):
    '''Base abstract class for Content snippets'''
    # common fields

    def template(self):
        '''Returns the template to be used to render the content'''
        raise NotImplementedError

    class Meta:
        abstract = True


class Text(Content):
    '''A block of text'''
    content = models.TextField(_('text'))

    def template(self):
        return 'text.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('text')
        verbose_name_plural = _('texts')


class Form(Content):
    '''A form registering input from the user'''
    # fields

    def template(self):
        return 'form.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('form')
        verbose_name_plural = _('forms')


class Image(Content):
    '''An image to be displayed'''
    content = FilerImageField(verbose_name=_('image'))

    def template(self):
        return 'image.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('image')
        verbose_name_plural = _('images')


class Video(Content):
    '''A video clip to be played'''
    content = FilerFileField(verbose_name=_('video'))

    def template(self):
        return 'video.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('video')
        verbose_name_plural = _('videos')


class Audio(Content):
    '''A piece of audio to be played'''
    content = FilerFileField(verbose_name=_('video'))

    def template(self):
        return 'audio.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('audioclip')
        verbose_name_plural = _('audioclips')


class File(Content):
    '''A file made available for download'''
    content = FilerFileField(verbose_name=_('file'), related_name='file_content')

    def template(self):
        return 'file.html'

    def __unicode__(self):
        return self

    class Meta:
        verbose_name = _('file')
        verbose_name_plural = _('files')
