# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

# import functools
import operator as oper


# def chain(func):
#     """
#     Function wrapper that clones and returns a new
#     instance of the class in order to make functions chainable.
#     """
#
#     @functools.wraps(func)
#     def wrapper(self, *args, **kwargs):
#         self = self.chain()
#         func(self, *args, **kwargs)
#         return self
#     return wrapper
#
#
# class Chainable(object):
#     """
#     A Base class which implements functionality
#     to clone itself with the @chain decorator
#     """
#     def chain(self):
#         klass = self.__class__.__new__(self.__class__)
#         klass.__dict__ = self.__dict__.copy()
#         return klass


class Expression(object):
    """
    Simple class for abstracting conditional expressions.
    Example:
        Expression(
            lhs="NOBODY expects the Spanish Inquisition!",
            operator="eq",
            rhs="NOBODY expects the Spanish Inquisition!"
        )

    Valid operators are eq, ne, lt, le, gt, ge and in.

    Expressions implements a __nonzero__ method and can therefore
    be used in boolean comparisons.

    Examples.
        if Expression(10, "gt", 9):
            <my code goes here>

        if Expression(True, "eq" True) & Expression("Foo", "ne", "Bar"):
            <something clever>
    """
    operators = {
        "eq": oper.eq,
        "ne": oper.ne,
        "lt": oper.lt,
        "le": oper.le,
        "gt": oper.gt,
        "ge": oper.ge,
        "in": oper.contains
    }

    def __init__(self, lhs, operator, rhs):

        self.lhs = lhs  # Left Hand Side
        self.rhs = rhs  # Right Hand Side

        try:
            self.operator = self.operators[operator.lower()]
        except KeyError:
            raise AttributeError("Invalid operator parameter. Valid operators are %s." %
                                 ", ".join(self.operators.keys()))

    def __repr__(self):
        return "<%(cls)s: %(lhs)s '%(operator)s' %(rhs)s>" % {
            "cls": self.__class__.__name__, "lhs": self.lhs,
            "operator": self.operator.__name__, "rhs": self.rhs
        }

    def __nonzero__(self):
        return self.eval
    __bool__ = __nonzero__

    @property
    def eval(self):
        return self.operator(self.lhs, self.rhs)


# class ExpressionEngine(Chainable):
#     """
#     A simple engine for evaluating expressions in the SERAF project
#
#     An expression consists of variables, operators and values.
#     Expressions can be chained using the binary operators `AND` or `OR`
#
#     is_valid = ExpressionEngine(expr).and_(expr2).or_(expr3).eval()
#
#     Example:
#         ($variable$ <operator> value) AND ($variable <operator> $variable)
#     """
#
#     def __init__(self, expr_obj):
#         self._expr = expr_obj
#
#     @property
#     def expr(self):
#         return self._expr
#
#     @expr.setter
#     def expr(self, expr):
#         self._expr = expr
#
#     @chain
#     def and_(self, expr):
#         self.expr = expr
#         return oper.and_(self.expr.eval, expr.eval)
#
#     @chain
#     def or_(self, expr):
#         return oper.or_(self.expr.eval, expr.eval)
#
#     def eval(self):
#         return self.expr.eval