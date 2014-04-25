from __future__ import unicode_literals
import copy
import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

from tokens.json_status import STATUS_OK
from tokens.tokens import token_generator
from vault.models import VaultUser


class TestVaultViews(TestCase):
    # def setUp(self):
    #     user_id = 1
    #     VaultUser.objects.get_or_create(id=user_id, email='post@inonit.no', phone='1234567890')
    #     self.post_data = {
    #         'user_id': user_id,
    #         'token': token_generator.make_token(user_id),
    #     }

    def test_vault_send_email(self):
        user_id = 1
        VaultUser.objects.get_or_create(id=user_id, email='post@inonit.no', phone='1234567890')
        post_data = {
            'user_id': user_id,
            'token': token_generator.make_token(user_id),
        }
        data = copy.copy(post_data)
        data.update(
            {
                'subject': '[Serafin] Test',
                'message': 'Test Message',
                'html_message': '<h1>Test message</h1>',
            }
        )
        client = Client()
        response = client.post(
            reverse('send_email', kwargs=post_data),
            data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('status'), STATUS_OK)

    def test_mirror_user(self):
        user_id = 2
        post_data = {
            'user_id': user_id,
            'token': token_generator.make_token(user_id),
        }
        data = copy.copy(post_data)
        data.update(
            {
                'email': 'test@inonit.no',
                'phone': '9876543210',
            }
        )
        client = Client()
        response = client.post(
            reverse('mirror_user', kwargs=post_data),
            data
        )

        VaultUser.objects.get(id=user_id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('status'), STATUS_OK)

    def test_delete_mirror(self):
        user_id = 3
        post_data = {
            'user_id': user_id,
            'token': token_generator.make_token(user_id),
        }
        data = copy.copy(post_data)
        data.update(
            {
                'email': 'test@inonit.no',
                'phone': '9876543210',
            }
        )
        client = Client()
        response = client.post(
            reverse('delete_mirror', kwargs=post_data),
            data
        )

        count = VaultUser.objects.filter(id=user_id).count()
        self.assertEqual(count, 0)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content).get('status'), STATUS_OK)
