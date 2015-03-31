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

    # "le" operator
    def test_expression_string_le(self):
        self.assertTrue(
            ord("a") <= ord("b")
        )
        self.assertTrue(Expression("a", "le", "a"))
        self.assertTrue(Expression("a", "le", "b"))
        self.assertFalse(Expression("b", "le", "a"))

    def test_expression_int_le(self):
        self.assertTrue(Expression(1, "le", 1))
        self.assertTrue(Expression(1, "le", 2))
        self.assertFalse(Expression(2, "le", 1))

    def test_expression_bool_le(self):
        self.assertTrue(Expression(False, "le", True))
        self.assertTrue(Expression(False, "le", False))
        self.assertTrue(Expression(True, "le", True))
        self.assertFalse(Expression(True, "le", False))

    # "gt" operator
    def test_expression_string_gt(self):
        self.assertTrue(
            ord("b") > ord("a")
        )
        self.assertTrue(Expression("b", "gt", "a"))
        self.assertFalse(Expression("a", "gt", "b"))

    def test_expression_int_gt(self):
        self.assertTrue(Expression(2, "gt", 1))
        self.assertFalse(Expression(1, "gt", 2))

    def test_expression_bool_gt(self):
        self.assertTrue(Expression(True, "gt", False))
        self.assertFalse(Expression(False, "gt", True))

    # "ge" operator
    def test_expression_string_ge(self):
        self.assertTrue(
            ord("b") >= ord("a")
        )
        self.assertTrue(Expression("a", "ge", "a"))
        self.assertTrue(Expression("b", "ge", "a"))
        self.assertFalse(Expression("a", "ge", "b"))

    def test_expression_int_ge(self):
        self.assertTrue(Expression(1, "ge", 1))
        self.assertTrue(Expression(2, "ge", 1))
        self.assertFalse(Expression(1, "ge", 2))

    def test_expression_bool_ge(self):
        self.assertTrue(Expression(True, "ge", False))
        self.assertTrue(Expression(False, "ge", False))
        self.assertTrue(Expression(True, "ge", False))
        self.assertFalse(Expression(False, "ge", True))

    # "in" operator
    def test_expression_string_in(self):
        self.assertTrue(Expression("The Castle of aaarrrrggh", "in", "aaarrrrggh"))
        self.assertFalse(Expression("The Castle of aaarrrrggh", "in", "AAARRRRGGH"))

    def test_expression_list_in(self):
        l = ["Blasphemy!", "He", "said", "it", "again"]
        self.assertTrue(Expression(l, "in", "Blasphemy!"))
        self.assertFalse(Expression(l, "in", "Parrot"))

    def test_expression_dict_in(self):
        d = {"a herring": "Then you must cut down the mightiest tree in the forest with..."}
        self.assertTrue(Expression(d, "in", "a herring"))
        self.assertFalse(Expression(d, "in", "an axe"))

    def test_expression_bool_in(self):
        self.assertTrue(Expression([True, False], "in", True))
        self.assertFalse(Expression([False], "in", True))