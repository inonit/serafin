# -*- coding: utf-8 -*-
"""
Serafin Expression mini-language implementation details.

Variables:
  Variables must be prefixed with `$` like eg. $MyLittlePony.
  Any variables must be predefined in the `system.models.Variable` Django model
  and will be looked up whenever encountered. If a variable is not found, an error
  will be raised.

Operators:
  We have two sets of expression types; MathExpressions and BoolExpressions.
  Expression evaluation between mixed types are not supported, and each Expression
  type supports a predefined set of operators.

  BoolExpression operators:
    - == (eq)   - >= (ge)
    - != (ne)   - in (in/contains)
    - <  (lt)   - &  (AND)
    - <= (le)   - |  (OR)
    - >  (gt)   - !  (NOT)


  MathExpression operators:
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
a User instance, attempts to lookup variables will raise an error.
"""

from __future__ import absolute_import, unicode_literals

import functools
import math
import operator as oper
from sys import float_info

from django.conf import settings
from django.utils import timezone
from django.utils.translation import ugettext as _
from pyparsing import (
    Literal, CaselessLiteral, Keyword, Word, Combine, Optional,
    ParseException, ZeroOrMore, Forward, Suppress, Group,
    alphas, alphanums, nums, oneOf, quotedString, removeQuotes,
    delimitedList, nestedExpr, sglQuotedString, dblQuotedString, commaSeparatedList,
    infixNotation, opAssoc
)
from system.models import Session, Variable


def chain(func):
    """
    Function wrapper that clones and returns a new
    instance of the class in order to make functions chainable.
    """

    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        self = self._clone(lhs=self.eval, operator=func(self, *args, **kwargs))
        return self

    return wrapper


@functools.total_ordering
class _Expression(object):
    """
    Base class for simple expressions.
    The class supports method chaining for defined operators.
    """

    operators = None

    def __init__(self, lhs, operator, rhs):

        self.lhs = lhs  # Left Hand Side
        self.rhs = rhs  # Right Hand Side

        try:
            self.operator = self._get_operator(operator.lower())
        except KeyError:
            raise AttributeError("Invalid operator parameter '%s'. Valid operators are %s." %
                                 (operator, ", ".join(self.operators.keys())))

    def __call__(self, param):
        """
        Sets the right hand parameter based on the output from
        the chained operator call.
        """
        self.rhs = getattr(param, "eval", param)
        return self

    @chain
    def __getattr__(self, name):
        """
        Returns the chained operator function
        """
        if name in self.operators:
            return self.operators[name]
        raise AttributeError(
            "'%(cls)s' object has no attribute '%(name)s'" % {
                "cls": self.__class__.__name__,
                "name": name
            })

    def __repr__(self):
        return "<%(cls)s: %(lhs)s '%(operator)s' %(rhs)s>" % {
            "cls": self.__class__.__name__, "lhs": self.lhs,
            "operator": self.operator.__name__, "rhs": self.rhs
        }

    def __eq__(self, other):
        return self.eval == other

    def __lt__(self, other):
        return self.eval < other

    def __nonzero__(self):
        return self.eval

    __bool__ = __nonzero__

    def _clone(self, **kwargs):
        """
        Returns a new clone of self with updated values
        from kwargs.
        """
        klass = self.__class__.__new__(self.__class__)
        klass.__dict__ = self.__dict__.copy()
        klass.__dict__.update(**kwargs)
        return klass

    def _get_operator(self, operator):
        if not self.operators:
            raise AttributeError(
                "%(cls)s has no attribute 'operators'. Define a %(cls)s.operators "
                "dictionary or override the `_get_operator()` function." % {
                    "cls": self.__class__.__name__
                }
            )
        return self.operators[operator]

    @property
    def eval(self):
        return self.operator(self.lhs, self.rhs)


class BoolExpression(_Expression):
    """
    Simple class for abstracting boolean expressions.
    Example:
        BoolExpression(
            lhs="NOBODY expects the Spanish Inquisition!",
            operator="eq",
            rhs="NOBODY expects the Spanish Inquisition!"
        ).eval

    Expressions can be chained ie. like this:
        BoolExpression(4, "gt", 3).and_(BoolExpression(["apple", "fish"], "in", "fish")).eval
        would evaluate to (4 > 3) and ("fish" in ["apple", "fish"])

    Valid operators are
      eq, ne, lt, le, gt, ge, in, contains (alias in), and_, or_.
    """
    operators = {
        "eq": oper.eq,
        "ne": oper.ne,
        "lt": oper.lt,
        "le": oper.le,
        "gt": oper.gt,
        "ge": oper.ge,
        "in": oper.contains,
        "contains": oper.contains,
        "and_": oper.and_,
        "or_": oper.or_,
        "not_": oper.not_
    }


class MathExpression(_Expression):
    """
    Simple class for abstracting simple mathematical expressions.
    Example:
        MathExpression(
            lhs=1,
            operator="add",
            rhs=2
        ).eval

    Expressions can be chained ie. like this:
        MathExpression(10, "add", 5).sub(1).div(MathExpression(1, "add", 1)).eval
        would evaluate to ((10 + 5) - 1) / (1 + 1)

    Valid operators are
      add, div, floordiv, pow, exponent (alias pow), mod,
      modulo (alias mod), multiply, sub, subtract (alias sub).
    """

    operators = {
        "add": oper.add,
        "div": oper.truediv,
        "floordiv": oper.floordiv,
        "pow": oper.pow,
        "exponent": oper.pow,
        "mod": oper.mod,
        "modulo": oper.mod,
        "multiply": oper.mul,
        "sub": oper.sub,
        "subtract": oper.sub
    }


class Parser(object):
    """
    A parser for parsing and evaluating expressions using our
    little expression mini-language.

    This code is pretty much stolen from
    https://pyparsing.wikispaces.com/file/view/fourFn.py
    """

    UNARY = "unary -"
    operators = {
        # Boolean operators
        "==": oper.eq, "!=": oper.ne, "<": oper.lt, "<=": oper.le,
        ">": oper.gt, ">=": oper.ge, "in": oper.contains, "&": oper.and_,
        "|": oper.or_, "!": oper.not_,

        # Mathematical operators
        "+": oper.add, "/": oper.truediv, "^": oper.pow,
        "%": oper.mod, "*": oper.mul, "-": oper.sub,
    }

    functions = {
        "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "abs": abs, "trunc": lambda a: int(a), "round": round,
        "sign": lambda a: abs(a) > float_info.epsilon and cmp(a, 0) or 0
    }

    constants = {
        "E": math.e, "PI": math.pi
    }

    bnf = None

    def __init__(self, user_obj=None):

        self.user = user_obj
        self.bnf = self._get_bnf()
        self.stack = []

    def _get_bnf(self):
        """
        Returns the `Backus–Naur Form` for the parser
        """
        if not self.bnf:
            # Operators
            exponent_operator = Literal("^")
            # negate_operator = Literal("!")  # TODO: Implement this so we can write `!True`
            multiply_operator = oneOf("* / %")
            add_operator = oneOf("+ -")
            comparison_operator = oneOf("== != < <= > >= & |") ^ Keyword("in")

            # Functions
            e = CaselessLiteral("E")
            pi = CaselessLiteral("PI")

            lparen, rparen, lbrack, rbrack = map(Suppress, "()[]")
            ident = Word(alphas, alphas + nums + "_$")
            variable = Combine(Literal("$") + Word(alphanums + "_"))
            boolean = Keyword("True") ^ Keyword("False")
            string = quotedString.setParseAction(removeQuotes)
            numeric = Combine(Word("+-" + nums, nums) +
                              Optional(Literal(".") + Optional(Word(nums))) +
                              Optional(e + Word("+-" + nums, nums)))

            expression = Forward()

            lists = Forward()
            lists << (delimitedList("," | string | numeric | variable | boolean |
                                    nestedExpr(lbrack, rbrack, content=lists)))

            atom = (Optional("-") +
                    (pi | e | numeric | ident + lparen + expression + rparen).setParseAction(self.push_stack)
                    | (variable | boolean | lists).setParseAction(self.push_stack)
                    | (lparen + expression.suppress() + rparen)).setParseAction(self.push_unary_stack)

            # By defining exponentiation as "atom [^factor]" instead of "atom [^atom],
            # we get left to right exponents. 2^3^2 = 2^(3^2), not (2^3)^2.
            factor = Forward()
            factor << atom + ZeroOrMore((exponent_operator + factor).setParseAction(self.push_stack))

            boolean = factor + ZeroOrMore((comparison_operator + factor).setParseAction(self.push_stack))
            term = boolean + ZeroOrMore((multiply_operator + boolean).setParseAction(self.push_stack))
            self.bnf = expression << term + ZeroOrMore((add_operator + term).setParseAction(self.push_stack))

        return self.bnf

    @property
    def userdata(self):
        """
        Returns a case insensitive copy of user.data if
        user is set, else just an empty dictionary
        """
        return self.user.data if self.user else {}

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
            return not self.user.is_anonymous() if self.user else False

        if variable == "enrolled":
            if "session" in self.userdata:
                session = Session.objects.get(id=self.userdata["session"])
                return session.program.programuseraccess_set.filter(user=self.user).exists()
            else:
                return False

        else:
            variable_obj = Variable.objects.filter(name=variable)
            if variable_obj.exists():
                variable_obj = variable_obj.get()
                return variable_obj.get_value() or ""

        return ""


    @staticmethod
    def _get_return_value(value):
        """
        Try to return the correct value type
        """
        # TODO: Django has some nice stuff for this we can steal. get_internal_type or something...
        try:
            if value.isnumeric():
                return float(value)
        except AttributeError:
            pass
        return value

    def push_stack(self, s, location, tokens):
        self.stack.append((tokens[0]))

    def push_unary_stack(self, s, location, tokens):
        if tokens and tokens[0] == "-":
            self.stack.append(self.UNARY)

    def evaluate_stack(self, expr):
        """
        Recursively reads the next expression from the stack.
        Looks up supported operators and/or functions and applies
        them.
        """
        operator = expr.pop()
        try:
            if operator == self.UNARY:
                return -self.evaluate_stack(expr)

            if operator in self.operators:
                rhs, lhs = self.evaluate_stack(expr), self.evaluate_stack(expr)
                if operator == "in":
                    rhs, lhs = lhs, rhs
                return self.operators[operator](lhs, rhs)
            elif operator in self.functions:
                return self.functions[operator](self.evaluate_stack(expr))
            elif operator in self.constants:
                return self.constants[operator]
            elif operator[0] == "$":
                variable = operator[1:]

                reserved_var = self._get_reserved_variable(variable)
                if reserved_var:
                    return reserved_var

                if not self.user:
                    raise ParseException("No user instance set. Please initialize the %s "
                                         "with a `user_obj` argument." % self.__class__.__name__)
                try:
                    value = self.userdata[variable]
                    if not value:
                        raise ValueError(_("Variable '%s' contains no value."))
                    return self._get_return_value(value)
                except KeyError:
                    raise ParseException(_("Undefined variable '%s'" % variable))
            elif operator in ("True", "False"):
                return True if operator == "True" else False
            else:
                return self._get_return_value(operator)
        except ValueError as e:
            raise ParseException(e)

    def parse(self, cmd_string):
        """
        Parse the command string and return the
        evaluated result.
        """
        self.bnf.parseString(cmd_string)
        return self.evaluate_stack(self.stack[:])
