from __future__ import unicode_literals
from django.core.mail.message import EmailMultiAlternatives
from django.utils.translation import ugettext_lazy as _

from django.db import models
from django.conf import settings
from twilio.rest import TwilioRestClient


class VaultUser(models.Model):
    '''Vault user corresponding to User with personal info'''

    email = models.EmailField(_('e-mail address'), max_length=254, blank=True)
    phone = models.CharField(_('phone number'), max_length=32, blank=True)
    # additional fields

    def send_sms(self, message=None):
        if message:
            client = TwilioRestClient(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            message = client.messages.create(
                body=message,
                to=self.phone,
                from_=settings.TWILIO_FROM_NUMBER,
            )

            return message.sid

        return None

    def send_email(self, subject=None, message=None, html_message=None):
        if subject and (message or html_message):
            subject = settings.EMAIL_SUBJECT_PREFIX + subject

            email = EmailMultiAlternatives(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [self.email]
            )

            if html_message:
                email.attach_alternative(html_message, 'text/html')

            return email.send()

        return None

    def __unicode__(self):
        return u'%s' % self.id

    class Meta:
        verbose_name = _('vault user')
        verbose_name_plural = _('vault users')
