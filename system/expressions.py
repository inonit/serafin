# -*- coding: utf-8 -*-
"""
Serafin Expression mini-language implementation details.

Variables:
  Variables must be prefixed with `$` like eg. $MyLittlePony.
  Any variables must be predefined in the `system.models.Variable` django model
  and will be looked up whenever encountered. If a variable is not found, an
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
    - >  (gt)


  MathExpression operators:
    - +  (add)              - %  (mod/modulo)
    - /  (truediv)          - *  (multiply)
    - // (floordiv)         - -  (subtract)
    - ^ (power/exponent)

Grouping:
  Expressions can be grouped by putting them in () parentheses.

Comments:
  Comments can be made by placing # before the line to ignore.

Evaluation of expressions.
  Once an expression has been parsed, it will instantiate either a BoolExpression
  or a MathExpression. It will build the chain according to expression grouping and return
  the value.
"""


from __future__ import absolute_import, unicode_literals

import functools
import operator as oper

from pyparsing import (
    Literal, CaselessLiteral, Word, Combine, Group, Keyword,
    Optional, ZeroOrMore, Forward, nums, alphas
)


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
        "or_": oper.or_
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

    Parses the input string and returns the parsed results ready
    for the interpreter to read.

    This code is pretty much stolen from
    https://pyparsing.wikispaces.com/file/view/fourFn.py
    """

    UNARY = "unary -"
    operators = {
        # Boolean operators
        # "==": oper.eq, "!=": oper.ne, "<": oper.lt, "<=": oper.le,
        # ">": oper.gt, ">=": oper.ge, "in": oper.contains, "&": oper.and_,
        # "|": oper.or_,

        # Mathematical operators
        "+": oper.add, "/": oper.truediv, "//": oper.floordiv, "^": oper.pow,
        "%": oper.mod, "*": oper.mul, "-": oper.sub
    }
    
    bnf = None

    def __init__(self, *args, **kwargs):

        self.bnf = self._get_bnf()
        self.stack = []
        
    def _get_bnf(self):
        """
        Returns the `Backus–Naur Form` for the parser
        """
        if not self.bnf:
            # eq = Literal("==")
            # ne = Literal("!=")
            # lt = Literal("<")
            # gt = Literal(">")
            # ge = Literal(">=")
            # in_ = Literal("in")
            # and_ = Literal("&")
            # or_ = Literal("|")

            add = Literal("+")
            div = Literal("/")
            floordiv = Literal("//")
            exponent = Literal("^")
            modulo = Literal("%")
            multiply = Literal("*")
            subtract = Literal("-")

            point = Literal(".")
            number = Combine(Word("+-" + nums, nums) + Optional(point + Optional(Word(nums))))
            variable = Keyword("$" + alphas + nums)
            lpar = Literal("(").suppress()
            rpar = Literal(")").suppress()
            multiply_operations = multiply | div | floordiv | modulo
            add_operations = add | subtract

            expression = Forward()
            atom = (Optional("-") + (number | variable + lpar + expression + rpar).setParseAction(self.push_stack)
                    | (lpar + expression.suppress() + rpar)).setParseAction(self.push_unary_stack)

            # By defining exponentiation as "atom [^factor]"
            # instead of "atom [^atom], we get left to right exponents.
            # 2^3^2 = 2^(3^2), not (2^3)^2.
            factor = Forward()
            factor << atom + ZeroOrMore((exponent + factor).setParseAction(self.push_stack))

            term = factor + ZeroOrMore((multiply_operations + factor).setParseAction(self.push_stack))
            self.bnf = expression << term + ZeroOrMore((add_operations + term).setParseAction(self.push_stack))
        return self.bnf

    def push_stack(self, s, location, tokens):
        self.stack.append((tokens[0]))

    def push_unary_stack(self, s, location, tokens):
        if tokens and tokens[0] == "-":
            self.stack.append(self.UNARY)

    def evaluate_stack(self, expr):
        operator = expr.pop()

        if operator == self.UNARY:
            return -self.evaluate_stack(expr)

        if operator in self.operators:
            rhs, lhs = self.evaluate_stack(expr), self.evaluate_stack(expr)
            return self.operators[operator](lhs, rhs)
        elif operator.startswith("$"):
            # look up variable
            pass
        elif operator[0].isalpha():
            return 0
        else:
            return float(operator)

    def parse(self, cmd_string):
        _ = self.bnf.parseString(cmd_string)
        return self.evaluate_stack(self.stack[:])
