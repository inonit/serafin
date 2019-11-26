# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals
from __future__ import division

from past.utils import old_div
import math

from django.test import TestCase
from django.utils import timezone

from users.models import User

from ..expressions import Parser


class ParserTestCase(TestCase):

    def setUp(self):
        self.user = User()
        self.user.data = {
            "UserVar1": 1,
            "UserVar2": 2,
            "UserVar3": "I like traffic lights",
            "UserVar4": ""
        }
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
        self.assertEqual(self.parser.parse("(9 + 3) / 11"), old_div((9 + 3.0), 11))
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
        self.assertEqual(self.parser.parse("PI*PI/10"), old_div(math.pi * math.pi, 10))
        self.assertEqual(self.parser.parse("PI * PI / 10"), old_div(math.pi * math.pi, 10))
        self.assertEqual(self.parser.parse("PI ^ 2"), math.pi ** 2)
        self.assertEqual(self.parser.parse("e / 3"), old_div(math.e, 3))
        self.assertEqual(self.parser.parse("E ^ pi"), math.e ** math.pi)
        self.assertEqual(self.parser.parse("6.02E23 * 8.048"), 6.02e23 * 8.048)

        # test functions
        self.assertEqual(self.parser.parse("round(PI^2)"), round(math.pi ** 2))
        self.assertEqual(self.parser.parse("sin(PI/2)"), math.sin(old_div(math.pi, 2)))
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
        # self.assertTrue(self.parser.parse("'1' in 'this is 1 brilliant string example'"))
        self.assertFalse(self.parser.parse("'brain' in 'my BRAIN hurts!'"))
        self.assertFalse(self.parser.parse("'what' in 'I really don't care...'"))
        # self.assertFalse(self.parser.parse("True in 'True, False'"))

        self.assertTrue(self.parser.parse("1 in [1,2,3]"))
        self.assertTrue(self.parser.parse("1 in [1, 2, 3]"))
        self.assertTrue(self.parser.parse("'a' in ['a', 'b']"))

        self.assertFalse(self.parser.parse("4 in [1, 2, 3]"))
        self.assertFalse(self.parser.parse("'c' in ['a', 'b']"))

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

        self.assertTrue(self.parser.parse("$registered == True"))
        self.assertFalse(self.parser.parse("$missing == 'something'"))
        self.assertTrue(self.parser.parse("($registered == True) | ($missing == 'something')"))
        self.assertTrue(self.parser.parse("($missing == 'something') | ($registered == True)"))
        self.assertFalse(self.parser.parse("($registered == True) & ($missing == 'something')"))
        self.assertFalse(self.parser.parse("($missing == 'something') & ($registered == True)"))

        self.assertTrue(self.parser.parse("$UserVar4 == ''"))
        self.assertTrue(self.parser.parse("$UserVar4 == 0"))
        self.assertTrue(self.parser.parse("$UserVar4 == []"))
        self.assertTrue(self.parser.parse("$UserVar4 == False"))
        self.assertTrue(self.parser.parse("$UserVar4 == None"))

        self.assertTrue(self.parser.parse("$missing == ''"))
        self.assertTrue(self.parser.parse("$missing == 0"))
        self.assertTrue(self.parser.parse("$missing == []"))
        self.assertTrue(self.parser.parse("$missing == False"))
        self.assertTrue(self.parser.parse("$missing == None"))
