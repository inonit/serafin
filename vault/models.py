from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models


class VaultUser(models.Model):
    '''Vault user corresponding to User with personal info'''
    email = models.EmailField(_('e-mail address'))
    phone = models.CharField(_('phone number'))
    # additional fields

    def __unicode__(self):
        return self.id

    class Meta:
        verbose_name = _('vault user')
        verbose_name_plural = _('vault users')
