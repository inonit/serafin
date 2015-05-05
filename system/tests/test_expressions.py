# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import math

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIRequestFactory

from users.models import User

from ..expressions import Parser, BoolExpression

factory = APIRequestFactory()


class BoolExpressionTestCase(TestCase):

    # "eq" operator
    def test_boolexpression_string_eq(self):
        self.assertTrue(BoolExpression(
            lhs="NOBODY expects the Spanish Inquisition!",
            operator="eq",
            rhs="NOBODY expects the Spanish Inquisition!"
        ))
        self.assertFalse(BoolExpression("Foo", "eq", "Bar"))

    def test_boolexpression_int_eq(self):
        self.assertTrue(BoolExpression(1, "eq", 1))
        self.assertFalse(BoolExpression(1, "eq", 2))

    def test_boolexpression_bool_eq(self):
        self.assertTrue(BoolExpression(True, "eq", True))
        self.assertFalse(BoolExpression(True, "eq", False))

    # "ne" operator
    def test_boolexpression_string_ne(self):
        self.assertTrue(BoolExpression("Foo", "ne", "Bar"))
        self.assertFalse(BoolExpression("Foo", "ne", "Foo"))

    def test_boolexpression_int_ne(self):
        self.assertTrue(BoolExpression(1, "ne", 2))
        self.assertFalse(BoolExpression(1, "ne", 1))

    def test_boolexpression_bool_ne(self):
        self.assertTrue(BoolExpression(True, "ne", False))
        self.assertFalse(BoolExpression(True, "ne", True))

    # "lt" operator
    def test_boolexpression_string_lt(self):
        # Strings are compared by ASCII values
        self.assertTrue(
            ord("a") < ord("b")
        )
        self.assertTrue(BoolExpression("a", "lt", "b"))
        self.assertFalse(BoolExpression("b", "lt", "a"))

    def test_boolexpression_int_lt(self):
        self.assertTrue(BoolExpression(1, "lt", 2))
        self.assertFalse(BoolExpression(1, "lt", 1))
        self.assertFalse(BoolExpression(2, "lt", 1))

    def test_boolexpression_bool_lt(self):
        self.assertTrue(BoolExpression(False, "lt", True))
        self.assertFalse(BoolExpression(True, "lt", False))

    # "le" operator
    def test_boolexpression_string_le(self):
        self.assertTrue(
            ord("a") <= ord("b")
        )
        self.assertTrue(BoolExpression("a", "le", "a"))
        self.assertTrue(BoolExpression("a", "le", "b"))
        self.assertFalse(BoolExpression("b", "le", "a"))

    def test_boolexpression_int_le(self):
        self.assertTrue(BoolExpression(1, "le", 1))
        self.assertTrue(BoolExpression(1, "le", 2))
        self.assertFalse(BoolExpression(2, "le", 1))

    def test_boolexpression_bool_le(self):
        self.assertTrue(BoolExpression(False, "le", True))
        self.assertTrue(BoolExpression(False, "le", False))
        self.assertTrue(BoolExpression(True, "le", True))
        self.assertFalse(BoolExpression(True, "le", False))

    # "gt" operator
    def test_boolexpression_string_gt(self):
        self.assertTrue(
            ord("b") > ord("a")
        )
        self.assertTrue(BoolExpression("b", "gt", "a"))
        self.assertFalse(BoolExpression("a", "gt", "b"))

    def test_boolexpression_int_gt(self):
        self.assertTrue(BoolExpression(2, "gt", 1))
        self.assertFalse(BoolExpression(1, "gt", 2))

    def test_boolexpression_bool_gt(self):
        self.assertTrue(BoolExpression(True, "gt", False))
        self.assertFalse(BoolExpression(False, "gt", True))

    # "ge" operator
    def test_boolexpression_string_ge(self):
        self.assertTrue(
            ord("b") >= ord("a")
        )
        self.assertTrue(BoolExpression("a", "ge", "a"))
        self.assertTrue(BoolExpression("b", "ge", "a"))
        self.assertFalse(BoolExpression("a", "ge", "b"))

    def test_boolexpression_int_ge(self):
        self.assertTrue(BoolExpression(1, "ge", 1))
        self.assertTrue(BoolExpression(2, "ge", 1))
        self.assertFalse(BoolExpression(1, "ge", 2))

    def test_boolexpression_bool_ge(self):
        self.assertTrue(BoolExpression(True, "ge", False))
        self.assertTrue(BoolExpression(False, "ge", False))
        self.assertTrue(BoolExpression(True, "ge", False))
        self.assertFalse(BoolExpression(False, "ge", True))

    # "in" operator
    def test_boolexpression_string_in(self):
        self.assertTrue(BoolExpression("The Castle of aaarrrrggh", "in", "aaarrrrggh"))
        self.assertFalse(BoolExpression("The Castle of aaarrrrggh", "in", "AAARRRRGGH"))

    def test_boolexpression_list_in(self):
        l = ["Blasphemy!", "He", "said", "it", "again"]
        self.assertTrue(BoolExpression(l, "in", "Blasphemy!"))
        self.assertFalse(BoolExpression(l, "in", "Parrot"))

    def test_boolexpression_dict_in(self):
        d = {"a herring": "Then you must cut down the mightiest tree in the forest with..."}
        self.assertTrue(BoolExpression(d, "in", "a herring"))
        self.assertFalse(BoolExpression(d, "in", "an axe"))

    def test_boolexpression_bool_in(self):
        self.assertTrue(BoolExpression([True, False], "in", True))
        self.assertFalse(BoolExpression([False], "in", True))

    # "and" operator
    def test_boolexpression_string_and(self):
        self.assertTrue(BoolExpression("fish" in ["apple", "fish"], "and_", True))
        self.assertFalse(BoolExpression("fish" in ["apple", "fish"], "and_", False))

    def test_boolexpression_int_and(self):
        self.assertTrue(BoolExpression(1 < 2, "and_", 10 < 20))
        self.assertFalse(BoolExpression(1 > 2, "and_", 10 < 20))

    def test_boolexpression_bool_and(self):
        self.assertTrue(BoolExpression(True, "and_", True))
        self.assertFalse(BoolExpression(False, "and_", True))

    # "or" operator
    def test_boolexpression_string_or(self):
        self.assertTrue(BoolExpression("fish" in ["apple"], "or_", "apple" in ["apple", "cake"]))
        self.assertFalse(BoolExpression("parrot" in ["I", "like", "rat", "cake"], "or_", False))

    # To be continued...

    def test_boolexpression_simple_chain(self):
        self.assertTrue(BoolExpression(True, "eq", True).and_(True))
        self.assertTrue(BoolExpression(True, "or_", False).or_(True))

    def test_boolexpression_complex_chain(self):
        self.assertTrue(BoolExpression(4, "gt", 3).and_(BoolExpression(["apple", "fish"], "in", "fish")))


class MathExpressionTestCase(TestCase):

    # TODO: Write me
    pass


class ParserTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(**{
            "username": 1,
            "data": {
                "UserVar1": 1,
                "UserVar2": 2,
                "UserVar3": "I like traffic lights",
                "UserVar4": ""
            }
        })
        self.parser = Parser(user_obj=self.user)
        self.now = timezone.localtime(timezone.now().replace(microsecond=0))

    def test_arithmetic_expressions(self):

        # test regular arithmetic operations
        self.assertEqual(self.parser.parse("9"), 9)
        self.assertEqual(self.parser.parse("-9"), -9)
        self.assertEqual(self.parser.parse("--9"), 9)
        self.assertEqual(self.parser.parse("9 + 3"), 9 + 3)
        self.assertEqual(self.parser.parse("9 + 3 + 6"), 9 + 3 + 6)
        self.assertEqual(self.parser.parse("9 + 3 / 11"), 9 + 3.0 / 11)
        self.assertEqual(self.parser.parse("(9 + 3)"), (9 + 3))
        self.assertEqual(self.parser.parse("(9 + 3) / 11"), (9 + 3.0) / 11)
        self.assertEqual(self.parser.parse("9 - 12 - 6"), 9 - 12 - 6)
        self.assertEqual(self.parser.parse("9 - (12 -6)"), 9 - (12 - 6))
        self.assertEqual(self.parser.parse("2 * 3"), 2 * 3)
        self.assertEqual(self.parser.parse("2 * 3.14159"), 2 * 3.14159)
        self.assertEqual(self.parser.parse("3.1415926535 * 3.1415926535 / 10"), 3.1415926535 * 3.1415926535 / 10)
        self.assertEqual(self.parser.parse("4 ^ 3"), 4 ** 3)
        self.assertEqual(self.parser.parse("4 ^ 2 ^ 3"), 4 ** 2 ** 3)
        self.assertEqual(self.parser.parse("4 ^ 2 ^ 3"), 4 ** (2 ** 3))
        self.assertEqual(self.parser.parse("(4 ^ 2) ^ 3"), (4 ** 2) ** 3)
        # self.assertEqual(self.parser.parse("1 + 2 + (-2 ^ 4)"), 1 + 2 + (-2 ** 4))  # This fails
        self.assertNotEqual(self.parser.parse("4 ^ 2 ^ 3"), (4 ** 2) ** 3)
        self.assertEqual(self.parser.parse("9 % 3"), 9 % 3)

        # test constants
        self.assertEqual(self.parser.parse("PI*PI/10"), math.pi * math.pi / 10)
        self.assertEqual(self.parser.parse("PI * PI / 10"), math.pi * math.pi / 10)
        self.assertEqual(self.parser.parse("PI ^ 2"), math.pi ** 2)
        self.assertEqual(self.parser.parse("e / 3"), math.e / 3)
        self.assertEqual(self.parser.parse("E ^ pi"), math.e ** math.pi)
        self.assertEqual(self.parser.parse("6.02E23 * 8.048"), 6.02e23 * 8.048)

        # test functions
        self.assertEqual(self.parser.parse("round(PI^2)"), round(math.pi ** 2))
        self.assertEqual(self.parser.parse("sin(PI/2)"), math.sin(math.pi / 2))
        self.assertEqual(self.parser.parse("trunc(E)"), int(math.e))
        self.assertEqual(self.parser.parse("trunc(-E)"), int(-math.e))
        self.assertEqual(self.parser.parse("round(E)"), round(math.e))
        self.assertEqual(self.parser.parse("round(-E)"), round(-math.e))
        self.assertEqual(self.parser.parse("sign(-2)"), -1)
        self.assertEqual(self.parser.parse("sign(0)"), 0)
        self.assertEqual(self.parser.parse("sign(0.1)"), 1)

    def test_boolean_expressions(self):
        self.assertTrue(self.parser.parse("True"))
        self.assertFalse(self.parser.parse("False"))
        self.assertTrue(self.parser.parse("True & True"))
        self.assertFalse(self.parser.parse("True & False"))
        self.assertTrue(self.parser.parse("(True | False) & True"))
        self.assertFalse(self.parser.parse("(True & False) | False"))

        # Negate is not yet implemented!
        # self.assertTrue(self.parser.parse("!False"))
        # self.assertFalse(self.parser.parse("!True"))
        # self.assertTrue(self.parser.parse("True & !False"))

        self.assertTrue(self.parser.parse("'brain' in 'my brain hurts!'"))
        self.assertFalse(self.parser.parse("'brain' in 'my BRAIN hurts!'"))
        self.assertFalse(self.parser.parse("'what' in 'I really don't care...'"))
        # self.assertTrue(self.parser.parse("'1' in 'this is 1 brilliant string example'"))  # fails
        # self.assertTrue(self.parser.parse("True in 'True, False'"))  # fails
        # self.assertTrue(self.parser.parse("1 in [1,2,3]"))  # fails

    def test_comparison_expressions(self):
        self.assertTrue(self.parser.parse("1 == 1"))
        self.assertTrue(self.parser.parse("(1 == 2) | (2 == 2)"))
        self.assertTrue(self.parser.parse("(1 - 1) == 0"))
        self.assertTrue(self.parser.parse("1 < 2"))
        self.assertTrue(self.parser.parse("(1 + 2 + 3) == (3 + 2 + 1)"))
        self.assertTrue(self.parser.parse("1 <= 1"))

    def test_date_expressions(self):
        self.assertTrue(self.parser.parse("'2014-12-31' < '2015-01-01'"))
        self.assertTrue(self.parser.parse("'2015-01-01' <= '2015-01-01'"))
        self.assertTrue(self.parser.parse("'2015-01-02' > '2015-01-01'"))
        self.assertTrue(self.parser.parse("'2015-01-02' >= '2015-01-02'"))
        self.assertTrue(self.parser.parse("'2015-02-01' > '2015-01-01'"))
        self.assertTrue(self.parser.parse("'2015-02-01' > '2015-01-02'"))
        self.assertTrue(self.parser.parse("'2015-01-01' == '2015-01-01'"))
        self.assertTrue(self.parser.parse("'2015-01-01' != '2015-01-02'"))
        self.assertTrue(self.parser.parse("'2015-01-01' < '2015-01-02' & True"))
        self.assertTrue(self.parser.parse("'2015-01-01' < '2015-01-02' | False"))
        self.assertTrue(self.parser.parse("('2015-01-01' < '2015-01-02') & True"))
        self.assertTrue(self.parser.parse("('2015-01-01' < '2015-01-02') | False"))
        self.assertTrue(self.parser.parse("('2015-01-10' > '2015-01-09') & ('2015-10-01' < '2015-11-01')"))
        self.assertTrue(self.parser.parse("('2015-02-10' > '2015-03-01') | ('2015-10-01' > '2015-09-01')"))
        # self.assertEqual(self.parser.parse("'2015-01-01' + '1d'"), "2015-01-02")  # not implemented
        # self.assertEqual(self.parser.parse("'2015-02-28' + '1d'"), "2015-03-01")  # not implemented
        # self.assertEqual(self.parser.parse("'2016-02-29' + '1d'"), "2016-02-29")  # not implemented
        # self.assertEqual(self.parser.parse("'2015-01-01' + '1m'"), "2015-02-01")  # not implemented
        # self.assertEqual(self.parser.parse("'2015-01-01' + '1y'"), "2016-01-01")  # not implemented
        # self.assertEqual(self.parser.parse("'2015-01-01' + '1y1m2d'"), "2016-02-03")  # not implemented

    def test_time_expressions(self):
        self.assertTrue(self.parser.parse("'12:00:00' > '11:00:00'"))
        self.assertTrue(self.parser.parse("'12:01:00' > '12:00:00'"))
        self.assertTrue(self.parser.parse("'12:00:01' > '12:00:00'"))
        self.assertTrue(self.parser.parse("'12:00:00' == '12:00:00'"))
        self.assertTrue(self.parser.parse("'12:10:00' >= '12:00:00'"))
        self.assertTrue(self.parser.parse("'12:00:00' < '13:00:00'"))
        self.assertTrue(self.parser.parse("'12:00:00' <= '13:00:00'"))
        self.assertTrue(self.parser.parse("'12:00:00' != '12:00:01'"))
        self.assertTrue(self.parser.parse("'12:00:00' > '11:00:00' & True"))
        self.assertTrue(self.parser.parse("'12:00:00' > '11:00:00' | False"))
        self.assertTrue(self.parser.parse("('12:00:00' > '11:00:00') & True"))
        self.assertTrue(self.parser.parse("('12:00:00' > '11:00:00') | False"))
        self.assertTrue(self.parser.parse("('12:00:00' < '13:00:00') & ('13:00:00' > '12:00:00')"))
        self.assertTrue(self.parser.parse("('12:00:00' > '13:00:00') | ('13:00:00' > '12:00:00')"))
        # self.assertEqual(self.parser.parse("'12:00:00' + '1h'"), "13:00:00")  # not implemented
        # self.assertEqual(self.parser.parse("'23:59:00' + '1m"), "00:00:00")  # not implemented
        # self.assertEqual(self.parser.parse("'12:00:00 + '1m'"), "12:01:00")  # not implemented
        # self.assertEqual(self.parser.parse("'12:00:00' + 1s"), "12:00:01")  # not implemented
        # self.assertEqual(self.parser.parse("'12:00:00' + '2h1m2s"), "14:01:02")  # not implemented

    def test_variable_expressions(self):
        # Reserved variables
        self.assertEqual(self.parser.parse("$current_date"), self.now.date().isoformat())
        self.assertEqual(self.parser.parse("$current_time"), self.now.time().isoformat())
        self.assertEqual(self.parser.parse("$current_day"), self.now.isoweekday())
        self.assertTrue(self.parser.parse("$registered"))
        self.assertFalse(self.parser.parse("$enrolled"))

        # User variables
        self.assertEqual(self.parser.parse("$UserVar1 + $UserVar2"), 3)
        self.assertRaises(TypeError, self.parser.parse, "$UserVar1 + $UserVar3")
