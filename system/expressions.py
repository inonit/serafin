# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import functools
import operator as oper

from django.core.exceptions import ImproperlyConfigured


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
            raise ImproperlyConfigured(
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

