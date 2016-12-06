from __future__ import unicode_literals
import json

from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock

from tokens.json_status import STATUS_OK, STATUS_INVALID_TOKEN

from tokens.tokens import token_generator
from vault.decorators import json_response
from vault.models import VaultUser


class TestJsonResponse(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = VaultUser.objects.create(email='post@inonit.no', phone='1234567890')

    # TODO: Fix these test cases. I don't quite see how they can work as only the request
    # is being created, not any response. Maybe use `rest_framework.tests.APITestCase` and
    # a real endpoint?

    # def test_okay(self):
    #     token = token_generator.make_token(self.user.pk)
    #
    #     func = Mock()
    #     decorated_func = json_response(func)
    #     request = self.factory.post(
    #         '/',
    #         {
    #             'user_id': self.user.pk,
    #             'token': token
    #         }
    #     )
    #     response = decorated_func(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content).get('status'), STATUS_OK)
    #
    # def test_invalid_token(self):
    #     token = 'invalidtoken'
    #
    #     func = Mock()
    #     decorated_func = json_response(func)
    #     request = self.factory.post(
    #         '/',
    #         {
    #             'user_id': self.user.pk,
    #             'token': token
    #         }
    #     )
    #     response = decorated_func(request)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(json.loads(response.content).get('status'), STATUS_INVALID_TOKEN)
