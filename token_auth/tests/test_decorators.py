from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.test import TestCase
from django.test.client import RequestFactory
from mock import Mock

from token_auth.decorators import token_required
from token_auth.tokens import token_generator


class TestTokenRequired(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()

    def test_okay(self):
        return_value = _('OK')
        user_id = 1
        token = token_generator.make_token(user_id)

        func = Mock(return_value=return_value)
        decorated_func = token_required(func)
        request = self.factory.get(
            '/',
            {
                'user_id': user_id,
                'token': token
            }
        )
        response = decorated_func(request)
        func.assert_called_with(request)
        self.assertEqual(response, return_value)

    def test_invalid_token(self):
        user_id = 1
        token = token_generator.make_token(3)  # Wrong token for user 1

        func = Mock()
        decorated_func = token_required(func)
        request = self.factory.get(
            '/',
            {
                'user_id': user_id,
                'token': token
            }
        )
        decorated_func(request)
        assert not func.called

    def test_no_user(self):
        user_id = 1
        token = token_generator.make_token(user_id)

        func = Mock()
        decorated_func = token_required(func)
        request = self.factory.get(
            '/',
            {
                'token': token
            }
        )
        decorated_func(request)
        assert not func.called

    def test_no_token(self):
        user_id = 1

        func = Mock()
        decorated_func = token_required(func)
        request = self.factory.get(
            '/',
            {
                'user_id': user_id
            }
        )
        decorated_func(request)
        assert not func.called

    def test_no_user_and_token(self):
        func = Mock()
        decorated_func = token_required(func)
        request = self.factory.get('/')
        decorated_func(request)
        assert not func.called