from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from system.models import Code

class CodeLog(models.Model):
    '''A model to keep track of Python code block result in admin interface'''

    content_type = models.ForeignKey(ContentType, verbose_name=_('sender'))
    object_id = models.PositiveIntegerField()
    sender = GenericForeignKey('content_type', 'object_id')
    subject = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('subject'), null=True, blank=True)

    code = models.ForeignKey(Code, verbose_name=_('code'))
    time = models.DateTimeField(_('time'))

    log = models.TextField(verbose_name=_('log'), null=True, blank=True)

    def __unicode__(self):
        return _('%(time)s: %(sender)s, %(code)s,python code result: %(log)s,') % {
            'time': self.time,
            'sender': self.sender,
            'code': self.code,
            'log': self.log,
        }

    class Meta:
        verbose_name = _('codelog')
        verbose_name_plural = _('codelogs')
