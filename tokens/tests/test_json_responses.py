from __future__ import unicode_literals
import json

from django.test import TestCase
from mock import Mock

from tokens.json_responses import JsonResponse


class TestJsonResponse(TestCase):
    def test_returns_json(self):
        return_value = {
            'item': 'One'
        }

        func = Mock(return_value=JsonResponse(content=return_value))
        response = func()
        self.assertEqual(response.get('Content-Type'), 'application/json')

    def test_converts_value_to_json(self):
        return_value = {
            'item': 'One'
        }

        func = Mock(return_value=JsonResponse(content=return_value))
        response = func()
        self.assertEqual(json.dumps(return_value), response.content)

    def test_handle_empty_values(self):
        return_value = None

        func = Mock(return_value=JsonResponse(content=return_value))
        response = func()
        self.assertEqual(json.dumps({}), response.content)
