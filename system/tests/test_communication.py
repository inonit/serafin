from django.test import TestCase
from django.conf import settings
from django.core.mail import send_mail
from users.models import User


class CommunicationTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(None, 'somepassword', settings.EMAIL_HOST_USER, settings.TEST_TO_SMS)

    def test_email_sending(self):
        email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
        return_value = self.user.send_email('Test Email', 'Test Body')
        settings.EMAIL_BACKEND = email_backend
        self.assertEqual(return_value, 1)

    def test_sms_sending(self):
        return_value = self.user.send_sms("this is test sms msg")
        self.assertIsNotNone(return_value)
        print("sms sid: {}".format(return_value))