from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from jsonfield import JSONField
from collections import OrderedDict


class Content(models.Model):
    '''A model containing page contents encoded as JSON data'''

    data = JSONField(load_kwargs={'object_pairs_hook': OrderedDict}, default='undefined')

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
