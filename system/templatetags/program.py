# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from django.template import Library, Node, TemplateSyntaxError, Variable

from ..models import Program

register = Library()


class BaseProgramNode(Node):
    """
    Base helper class for handling the program template tags.
    """

    def __init__(self, object_expr, as_varname):
        self.model = Program
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

    def get_context_value_from_queryset(self, context, queryset):
        """
        Subclasses should override this.
        """
        raise NotImplementedError

    def render(self, context):
        queryset = self.get_queryset(context)
        context[self.as_varname] = self.get_context_value_from_queryset(context, queryset)

    def get_queryset(self, context):
        user_obj = self.object_expr.resolve(context, ignore_failures=True)
        queryset = self.model.objects.all()
        if not user_obj:
            return queryset.none()
        if not user_obj.is_staff:
            queryset = queryset.filter(
                pk__in=user_obj.programuseraccess_set.values_list("program", flat=True)
            )
        if user_obj.program_restrictions.exists():
            program_ids = user_obj.program_restrictions.values_list('id')
            queryset = queryset.filter(id__in=program_ids)
        return queryset


class CurrentProgramNode(BaseProgramNode):
    """
    Insert a program instance into the context
    """
    def get_context_value_from_queryset(self, context, queryset):
        request = Variable("request").resolve(context)
        if "_program_id" in request.session:
            try:
                return queryset.get(pk=request.session["_program_id"])
            except self.model.DoesNotExist:
                pass


class ListProgramNode(BaseProgramNode):
    """
    Insert a list of programs into the context
    """
    def get_context_value_from_queryset(self, context, queryset):
        return list(queryset)


@register.tag
def get_current_program(parser, token):
    """
    Get the currently active program if any and populates the
    template context with a variable containing the `Program` instance.

    Syntax::
        {% get_current_program for [user instance] as [varname] %}

    """
    return CurrentProgramNode.handle_token(parser, token)

@register.tag
def get_available_programs(parser, token):
    """
    Returns a list of available programs for the given params and
    populates the template context with a variable containing that
    value.

    Syntax::
        {% get_available_programs for [user instance] as [variable] %}
        {% for program in [variable] %}
            ...
        {% endfor %}
    """
    return ListProgramNode.handle_token(parser, token)
