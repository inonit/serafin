# -*- coding: utf-8 -*-
"""
Serafin Parser mini-language implementation details.

Variables:
  Variables must be prefixed with `$` like eg. $MyLittlePony.
  Any variables must be predefined in the `system.models.Variable` Django model
  and will be looked up whenever encountered. If a variable is not found, an error
  will be raised.

Operators:
  We have two sets of expression types; math expressions and boolean expressions.
  Expression evaluation between mixed types are not supported, and each expression
  type supports a predefined set of operators.

  Boolean expression operators:
    - == (eq)   - >= (ge)
    - != (ne)   - in (in/contains)
    - <  (lt)   - &  (AND)
    - <= (le)   - |  (OR)
    - >  (gt)   - !  (NOT)

  Math expression operators:
    - +  (add)              - %  (mod/modulo)
    - /  (truediv)          - *  (multiply)
    - ^  (power/exponent)   - -  (subtract)

Functions:
  The following mathematical functions are available. They must bw written lowercase,
  and takes a single numeric argument. Constants can be also be used as argument.
    - sin   - cos   - tan
    - abs   - trunc - round
    - sign

Constants:
  Supported constants are E and PI.
    - E provides the mathematical constant E (2.718281... to available precision)
    - PI provides the mathematical constant π (3.141592... to available precission)

Grouping:
  Expressions can be grouped by putting them in () parentheses.


In order to resolve user variables, a User instance must be passed
to the Parser on initialization. If the Parser is initialized without
a User instance, attempts to lookup undefined variables will raise an error.
"""

from __future__ import absolute_import, unicode_literals

from past.builtins import cmp
from builtins import str
from builtins import map
from builtins import object
import math
import operator as oper
from sys import float_info

from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import ugettext as _
from pyparsing import (
    Literal, CaselessLiteral, Keyword, Word, Combine, Optional,
    ParseException, ZeroOrMore, Forward, Suppress, Group,
    alphas, alphanums, nums, oneOf, quotedString, removeQuotes,
    delimitedList, ParseResults
)


def str_trim_float(value):
    """Convert value to string"""
    if isinstance(value, float):
        value = str(value)
        if value.endswith('.0'):
            return value[:-2]
        return value
    return str(value)


class Parser(object):
    """
    A parser for parsing and evaluating expressions using our
    little expression mini-language.

    This code is partially taken from
    https://pyparsing.wikispaces.com/file/view/fourFn.py
    and other pyparsing examples
    """

    UNARY = "unary -"
    INDEXED_VARIABLE = "var idx"
    NOT = "!"

    bool_operators = {
        "==": oper.eq, "!=": oper.ne, "<": oper.lt, "<=": oper.le,
        ">": oper.gt, ">=": oper.ge, "in": oper.contains, "&": oper.and_,
        "|": oper.or_, "!": oper.not_,
    }
    math_operators = {
        "+": oper.add, "/": oper.truediv, "^": oper.pow,
        "%": oper.mod, "*": oper.mul, "-": oper.sub,
    }

    operators = {}
    operators.update(bool_operators)
    operators.update(math_operators)

    functions = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "abs": abs, "trunc": lambda a: int(a), "round": round,
        "sign": lambda a: abs(a) > float_info.epsilon and cmp(a, 0) or 0,
        "str": str_trim_float,
    }

    constants = {
        "E": math.e, "PI": math.pi
    }

    bnf = None

    def __init__(self, user_obj=None):

        self.user = user_obj
        self.bnf = self._get_bnf()
        self.stack = []

        from system.models import Variable
        predefined_vars = Variable.objects.filter(
            Q(value__isnull=False) | Q(random_type__isnull=False)
        )
        predefined_values = {var.name: var.get_value() for var in predefined_vars}
        predefined_values.update(self.user.data)

        self.userdata = predefined_values

    def _get_bnf(self):
        """
        Returns the `Backus–Naur Form` for the parser
        """
        if not self.bnf:
            # Operators
            exponent_operator = Literal("^")
            negate_operator = Literal("!")
            multiply_operator = oneOf("* / %")
            add_operator = oneOf("+ -")
            comparison_operator = oneOf("== != < <= > >= & |") ^ Keyword("in")

            # Functions
            e = CaselessLiteral("E")
            pi = CaselessLiteral("PI")

            lparen, rparen, lbrack, rbrack = list(map(Suppress, "()[]"))
            ident = Word(alphas, alphas + nums + "_$")
            variable = Combine(Literal("$") + Word(alphanums + "_"))
            boolean = Keyword("True") ^ Keyword("False")
            string = quotedString.setParseAction(removeQuotes)
            numeric = Combine(Word("+-" + nums, nums) +
                              Optional(Literal(".") + Optional(Word(nums))) +
                              Optional(e + Word("+-" + nums, nums)))
            none = Keyword("None")

            expression = Forward()

            lists = Forward()
            lists << (lbrack + Optional(delimitedList(numeric ^ variable ^ boolean ^ string)) + rbrack)

            atom = (Optional("-") +
                    (pi | e | numeric | ident + lparen + expression + rparen).setParseAction(self.push_stack)
                    | (variable + lbrack + expression + rbrack).setParseAction(self.push_array_variable)
                    | (variable | none | boolean | string | Group(lists)).setParseAction(self.push_stack)
                    | Optional(negate_operator) + (lparen + expression.suppress() + rparen)).setParseAction(self.push_unary_stack)

            # By defining exponentiation as "atom [^factor]" instead of "atom [^atom],
            # we get left to right exponents. 2^3^2 = 2^(3^2), not (2^3)^2.
            factor = Forward()
            factor << atom + ZeroOrMore((exponent_operator + factor).setParseAction(self.push_stack))

            boolean = factor + ZeroOrMore((comparison_operator + factor).setParseAction(self.push_stack))
            term = boolean + ZeroOrMore((multiply_operator + boolean).setParseAction(self.push_stack))
            self.bnf = expression << term + ZeroOrMore((add_operator + term).setParseAction(self.push_stack))

        return self.bnf

    @property
    def reserved_variables(self):
        """
        Returns a subset of the SYSTEM_VARIABLES list with
        only items which has "user" in it's domain list.
        """
        variables = getattr(settings, "RESERVED_VARIABLES", {})
        return [v for v in variables if "domains" in v and "user" in v["domains"]]

    def _get_reserved_variable(self, variable):
        """
        Returns the value of a reserved variable
        """
        now = timezone.localtime(timezone.now().replace(microsecond=0))

        if variable == "current_day":
            return now.isoweekday()

        if variable == "current_time":
            return now.time().isoformat()

        if variable == "current_date":
            return now.date().isoformat()

        if variable == "registered":
            return not self.user.is_anonymous if self.user else False

        if variable == "enrolled":
            if "session" in self.userdata:
                from system.models import Session
                session = Session.objects.get(id=self.userdata["session"])
                return session.program.programuseraccess_set.filter(user=self.user).exists()
            else:
                return False

        return ""

    @staticmethod
    def _get_return_value(value):
        """
        Try to return the correct value type
        """
        # TODO: Django has some nice stuff for this we can steal. get_internal_type or something...
        try:
            return float(value)
        except (ValueError, TypeError):
            pass
        if value in ("True", "False"):
            return True if value == "True" else False
        return value

    def push_stack(self, s, location, tokens):
        self.stack.append((tokens[0]))

    def push_unary_stack(self, s, location, tokens):
        if tokens and tokens[0] == "-":
            self.stack.append(self.UNARY)
        elif tokens and tokens[0] == "!":
            self.stack.append(self.NOT)

    def push_array_variable(self, s, location, tokens):
        self.stack.append(tokens[0])
        self.stack.append(self.INDEXED_VARIABLE)

    def evaluate_stack(self, expr):
        """
        Recursively reads the next expression from the stack.
        Looks up supported operators and/or functions and applies
        them.
        """
        operator = expr.pop()
        if operator == self.UNARY:
            return -self.evaluate_stack(expr)
        elif operator == self.NOT:
            return not self.evaluate_stack(expr)

        if operator in self.operators:
            rhs, lhs = self.evaluate_stack(expr), self.evaluate_stack(expr)
            if operator in self.bool_operators:
                if not rhs:
                    rhs = False
                if not lhs:
                    lhs = False
            if operator == "in":
                rhs, lhs = lhs, rhs
            if isinstance(lhs, ParseResults):
                lhs = [self._get_return_value(item) for item in lhs]
            return self.operators[operator](lhs, rhs)
        elif operator in self.functions:
            return self.functions[operator](self.evaluate_stack(expr))
        elif operator in self.constants:
            return self.constants[operator]
        elif operator and (operator[0] == "$" or operator == self.INDEXED_VARIABLE):
            variable_index = None
            if operator == self.INDEXED_VARIABLE:
                operator = expr.pop()
                variable_index = self.evaluate_stack(expr)
            variable = operator[1:]

            if variable in [v["name"] for v in self.reserved_variables]:
                return self._get_reserved_variable(variable)

            if not self.user:
                raise ParseException("No user instance set. Please initialize the %s "
                                     "with a `user_obj` argument." % self.__class__.__name__)

            variable_value = self._get_return_value(self.userdata.get(variable))
            if variable_index is not None:
                from system.models import Variable
                if Variable.is_array_variable(variable):
                    return self._get_return_value(variable_value[int(variable_index)])
            else:
                from system.models import Variable
                if Variable.is_array_variable(variable) and isinstance(variable_value, list):
                    variable_value = self._get_return_value(variable_value[-1])
            return variable_value

        elif operator in ("True", "False"):
            return True if operator == "True" else False
        elif operator == "None":
            return None
        else:
            return self._get_return_value(operator)

    def parse(self, cmd_string):
        """
        Parse the command string and return the
        evaluated result.
        """
        self.bnf.parseString(cmd_string)
        return self.evaluate_stack(self.stack[:])
