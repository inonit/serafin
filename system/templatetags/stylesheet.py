# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.template import Library, Node, TemplateSyntaxError, Variable

register = Library()


class StylesheetNode(Node):
    """
    Base helper class for handling the stylesheet template tags.
    """

    def __init__(self, object_expr, as_varname):
        self.object_expr = object_expr
        self.as_varname = as_varname

    @classmethod
    def handle_token(cls, parser, token):
        tokens = token.contents.split()
        if tokens[1] != "for":
            raise TemplateSyntaxError("Second argument in %r tag must be 'for'." % tokens[0])

        if len(tokens) == 5:
            if tokens[3] != "as":
                raise TemplateSyntaxError("Third argument in %r tag must be 'as'." % tokens[0])
            return cls(object_expr=parser.compile_filter(tokens[2]), as_varname=tokens[4])
        else:
            raise TemplateSyntaxError("%r tag requires exactly 4 arguments.")

    def get_context_value(self, context, iterable):
        """
        Subclasses should override this.
        """
        raise NotImplementedError

    def render(self, context):
        stylesheets = self.stylesheet_list(context)
        context[self.as_varname] = self.get_context_value(context, stylesheets)

    def stylesheet_list(self, context):
        """
        Returns the full list of all available stylesheets.
        Any filtering on permissions and such could be done in
        this method.
        """
        return getattr(settings, "STYLESHEETS", [])


class CurrentStylesheetNode(StylesheetNode):
    """
    Insert a program instance into the context
    """
    def get_context_value(self, context, iterable):
        request = Variable("request").resolve(context)
        if "_stylesheet" in request.session:
            stylesheet = request.session["_stylesheet"]
            stylesheets = self.stylesheet_list(context)
            if stylesheet in [s["name"] for s in stylesheets]:
                for i, s in enumerate(stylesheets):
                    if s["name"] == stylesheet:
                        return stylesheets[i]


class ListStylesheetNode(StylesheetNode):
    """
    Insert a list of programs into the context
    """
    def get_context_value(self, context, iterable):
        return list(iterable)


@register.tag
def get_current_stylesheet(parser, token):
    """
    Get the currently active stylesheet if any and populates the
    template context with a variable containing the stylesheet path.

    Syntax::
        {% get_current_stylesheet for [user instance] as [varname] %}

    """
    return CurrentStylesheetNode.handle_token(parser, token)

@register.tag
def get_available_stylesheets(parser, token):
    """
    Returns a list of available stylesheets for the given params and
    populates the template context with a variable containing that
    value.

    Syntax::
        {% get_available_stylesheets for [user instance] as [variable] %}
        {% for program in [variable] %}
            ...
        {% endfor %}
    """
    return ListStylesheetNode.handle_token(parser, token)
