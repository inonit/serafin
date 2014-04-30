from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from jsonfield import JSONField
from collections import OrderedDict
from system.models import Variable, Part


class Content(models.Model):
    '''A model containing page contents encoded as JSON data'''

    title = models.CharField(_('title'), max_length=64, blank=True, unique=True)
    part = models.ForeignKey(Part, verbose_name=_('part'), null=True, blank=True)
    admin_note = models.TextField(_('admin note'), blank=True)

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='''
        [{
            content_type: 'text',
            content: {
                text: '',
                html: '',
            }
        }]
    ''')

    vars_used = models.ManyToManyField(Variable, editable=False)

    def __unicode__(self):
        output = _('No content')

        try:
            output = self.data[0]['content'][:50] + '...'
        except:
            pass

        return output

    class Meta:
        abstract = True
        verbose_name = _('content')
        verbose_name_plural = _('contents')


class Email(Content):
    '''A model for e-mail content'''

    class Meta:
        verbose_name = _('e-mail')
        verbose_name_plural = _('e-mails')


class SMS(Content):
    '''A model for SMS content'''

    class Meta:
        verbose_name = _('SMS')
        verbose_name_plural = _('SMSs')
