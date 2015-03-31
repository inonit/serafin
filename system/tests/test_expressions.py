# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.test import TestCase

from ..expressions import Expression


class ExpressionTestCase(TestCase):

    # "eq" operator
    def test_expression_string_eq(self):
        self.assertTrue(Expression(
            lhs="NOBODY expects the Spanish Inquisition!",
            operator="eq",
            rhs="NOBODY expects the Spanish Inquisition!"
        ))
        self.assertFalse(Expression("Foo", "eq", "Bar"))

    def test_expression_int_eq(self):
        self.assertTrue(Expression(1, "eq", 1))
        self.assertFalse(Expression(1, "eq", 2))

    def test_expression_bool_eq(self):
        self.assertTrue(Expression(True, "eq", True))
        self.assertFalse(Expression(True, "eq", False))

    # "ne" operator
    def test_expression_string_ne(self):
        self.assertTrue(Expression("Foo", "ne", "Bar"))
        self.assertFalse(Expression("Foo", "ne", "Foo"))

    def test_expression_int_ne(self):
        self.assertTrue(Expression(1, "ne", 2))
        self.assertFalse(Expression(1, "ne", 1))

    def test_expression_bool_ne(self):
        self.assertTrue(Expression(True, "ne", False))
        self.assertFalse(Expression(True, "ne", True))

    # "lt" operator
    def test_expression_string_lt(self):
        # Strings are compared by ASCII values
        self.assertTrue(
            ord("a") < ord("b")
        )
        self.assertTrue(Expression("a", "lt", "b"))
        self.assertFalse(Expression("b", "lt", "a"))

    def test_expression_int_lt(self):
        self.assertTrue(Expression(1, "lt", 2))
        self.assertFalse(Expression(1, "lt", 1))
        self.assertFalse(Expression(2, "lt", 1))

    def test_expression_bool_lt(self):
        self.assertTrue(Expression(False, "lt", True))
        self.assertFalse(Expression(True, "lt", False))


