# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from django.test import TestCase

from ..expressions import BoolExpression


class BoolExpressionTestCase(TestCase):

    # "eq" operator
    def test_expression_string_eq(self):
        self.assertTrue(BoolExpression(
            lhs="NOBODY expects the Spanish Inquisition!",
            operator="eq",
            rhs="NOBODY expects the Spanish Inquisition!"
        ))
        self.assertFalse(BoolExpression("Foo", "eq", "Bar"))

    def test_expression_int_eq(self):
        self.assertTrue(BoolExpression(1, "eq", 1))
        self.assertFalse(BoolExpression(1, "eq", 2))

    def test_expression_bool_eq(self):
        self.assertTrue(BoolExpression(True, "eq", True))
        self.assertFalse(BoolExpression(True, "eq", False))

    # "ne" operator
    def test_expression_string_ne(self):
        self.assertTrue(BoolExpression("Foo", "ne", "Bar"))
        self.assertFalse(BoolExpression("Foo", "ne", "Foo"))

    def test_expression_int_ne(self):
        self.assertTrue(BoolExpression(1, "ne", 2))
        self.assertFalse(BoolExpression(1, "ne", 1))

    def test_expression_bool_ne(self):
        self.assertTrue(BoolExpression(True, "ne", False))
        self.assertFalse(BoolExpression(True, "ne", True))

    # "lt" operator
    def test_expression_string_lt(self):
        # Strings are compared by ASCII values
        self.assertTrue(
            ord("a") < ord("b")
        )
        self.assertTrue(BoolExpression("a", "lt", "b"))
        self.assertFalse(BoolExpression("b", "lt", "a"))

    def test_expression_int_lt(self):
        self.assertTrue(BoolExpression(1, "lt", 2))
        self.assertFalse(BoolExpression(1, "lt", 1))
        self.assertFalse(BoolExpression(2, "lt", 1))

    def test_expression_bool_lt(self):
        self.assertTrue(BoolExpression(False, "lt", True))
        self.assertFalse(BoolExpression(True, "lt", False))

    # "le" operator
    def test_expression_string_le(self):
        self.assertTrue(
            ord("a") <= ord("b")
        )
        self.assertTrue(BoolExpression("a", "le", "a"))
        self.assertTrue(BoolExpression("a", "le", "b"))
        self.assertFalse(BoolExpression("b", "le", "a"))

    def test_expression_int_le(self):
        self.assertTrue(BoolExpression(1, "le", 1))
        self.assertTrue(BoolExpression(1, "le", 2))
        self.assertFalse(BoolExpression(2, "le", 1))

    def test_expression_bool_le(self):
        self.assertTrue(BoolExpression(False, "le", True))
        self.assertTrue(BoolExpression(False, "le", False))
        self.assertTrue(BoolExpression(True, "le", True))
        self.assertFalse(BoolExpression(True, "le", False))

    # "gt" operator
    def test_expression_string_gt(self):
        self.assertTrue(
            ord("b") > ord("a")
        )
        self.assertTrue(BoolExpression("b", "gt", "a"))
        self.assertFalse(BoolExpression("a", "gt", "b"))

    def test_expression_int_gt(self):
        self.assertTrue(BoolExpression(2, "gt", 1))
        self.assertFalse(BoolExpression(1, "gt", 2))

    def test_expression_bool_gt(self):
        self.assertTrue(BoolExpression(True, "gt", False))
        self.assertFalse(BoolExpression(False, "gt", True))

    # "ge" operator
    def test_expression_string_ge(self):
        self.assertTrue(
            ord("b") >= ord("a")
        )
        self.assertTrue(BoolExpression("a", "ge", "a"))
        self.assertTrue(BoolExpression("b", "ge", "a"))
        self.assertFalse(BoolExpression("a", "ge", "b"))

    def test_expression_int_ge(self):
        self.assertTrue(BoolExpression(1, "ge", 1))
        self.assertTrue(BoolExpression(2, "ge", 1))
        self.assertFalse(BoolExpression(1, "ge", 2))

    def test_expression_bool_ge(self):
        self.assertTrue(BoolExpression(True, "ge", False))
        self.assertTrue(BoolExpression(False, "ge", False))
        self.assertTrue(BoolExpression(True, "ge", False))
        self.assertFalse(BoolExpression(False, "ge", True))

    # "in" operator
    def test_expression_string_in(self):
        self.assertTrue(BoolExpression("The Castle of aaarrrrggh", "in", "aaarrrrggh"))
        self.assertFalse(BoolExpression("The Castle of aaarrrrggh", "in", "AAARRRRGGH"))

    def test_expression_list_in(self):
        l = ["Blasphemy!", "He", "said", "it", "again"]
        self.assertTrue(BoolExpression(l, "in", "Blasphemy!"))
        self.assertFalse(BoolExpression(l, "in", "Parrot"))

    def test_expression_dict_in(self):
        d = {"a herring": "Then you must cut down the mightiest tree in the forest with..."}
        self.assertTrue(BoolExpression(d, "in", "a herring"))
        self.assertFalse(BoolExpression(d, "in", "an axe"))

    def test_expression_bool_in(self):
        self.assertTrue(BoolExpression([True, False], "in", True))
        self.assertFalse(BoolExpression([False], "in", True))
