from __future__ import unicode_literals
import copy
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from token_auth.json_status import STATUS_OK
from token_auth.tokens import token_generator
from vault.models import VaultUser


class TestVaultViews(TestCase):
    def setUp(self):
        user_id = 1
        VaultUser.objects.get_or_create(id=user_id, email='allen.machary@gmail.com', phone='1234567890')
        self.post_data = {
            'user_id': user_id,
            'token': token_generator.make_token(user_id),
        }

    def test_vault_send_email(self):
        data = copy.copy(self.post_data)
        data.update(
            {
                'subject': '[Seraf] Test',
                'message': 'Test Message',
                'html_message': '<h1>Test message</h1>',
            }
        )
        client = Client()
        response = client.post(
            reverse('send_email', kwargs=self.post_data),
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('status'), STATUS_OK)