from __future__ import unicode_literals
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin


class UserManager(BaseUserManager):
    '''Custom User model Manager'''

    def create_user(self, password):
        user = self.model()
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, password):
        user = self.create_user(password=password)
        user.is_admin = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    '''Custom User, identified by ID and password'''

    is_staff = models.BooleanField(_('staff'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    date_joined = models.DateTimeField(_('registration time'), auto_now_add=True, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'

    @property
    def username(self):
        return _('User %i' % self.id)

    def __unicode__(self):
        return self.username

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')


class UserField(models.Model):
    '''A simple modelling of User key: value relationships'''

    user = models.ForeignKey(User, verbose_name=_('user'))
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64, blank=True)

    def __unicode__(self):
        return '%s: %s' % (self.key, self.value)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')