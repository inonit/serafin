# from __future__ import unicode_literals
#
# from django.test import TestCase
# from mock import Mock
#
# from users.decorators import vault_post
#
#
# class TestVaultPost(TestCase):
#     # def setUp(self):
#     #     # Every test needs access to the request factory.
#     #     self.factory = RequestFactory()
#
#     def test_okay(self):
#         url, user_id, token = '/vault/api/test/', '1', 'usertoken'
#
#         func = Mock(return_value=(url, user_id, token))
#         decorated_func = vault_post(func)
#         response = decorated_func('param')
#
#         self.assertEqual(response, True)