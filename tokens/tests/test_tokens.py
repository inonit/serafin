from __future__ import unicode_literals
from datetime import date, timedelta

from django.test import TestCase

from tokens.tokens import token_generator


class TestTokenGenerator(TestCase):

    def test_today(self):
        today = date.today()
        self.assertEqual(token_generator._today(), today)

    def test_today_past_date(self):
        day = date.today() - timedelta(days=3)
        self.assertNotEqual(token_generator._today(), day)

    def test_today_future_date(self):
        day = date.today() + timedelta(days=4)
        self.assertNotEqual(token_generator._today(), day)

    def test_num_days(self):
        days = 7
        dt = date(2001, 1, 1) + timedelta(days=days)
        self.assertEqual(token_generator._num_days(dt), days)

    def test_make_token(self):
        user_id = 1
        self.assertIsInstance(token_generator.make_token(user_id), str)

    def test_check_token_okay(self):
        user_id = 1
        token = token_generator.make_token(user_id)
        self.assertEqual(token_generator.check_token(user_id, token), True)

    def test_check_token_fail(self):
        user_id = 3
        token = token_generator.make_token(1)
        self.assertEqual(token_generator.check_token(user_id, token), False)

    def test_check_token_expired(self):
        user_id = 1
        timestamp = (date.today() - timedelta(days=8)).day
        old_token = token_generator._make_token_with_timestamp(user_id, timestamp)
        self.assertEqual(token_generator.check_token(user_id, old_token), False)

    def test_check_token_future_timestamp(self):
        user_id = 1
        timestamp = (date.today() + timedelta(days=4)).day
        future_token = token_generator._make_token_with_timestamp(user_id, timestamp)
        self.assertEqual(token_generator.check_token(user_id, future_token), False)
