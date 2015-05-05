# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import textwrap

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated

from .models import Program, Variable
from .serializers import VariableSerializer, ExpressionSerializer
from .filters import VariableSearchFilter

import re


@staff_member_required
def export_text(request):
    '''
    Iterates through all content in a Program and exports translatable text.
    TRANSLATION is a copy of ORIGINAL to help translators retain markdown
    and variable replacement syntax.
    '''

    queryset = Program.objects.get(id__in=ids)

    def indent(string):
        '''Helper for prettier code in format_field and format_content'''
        # Number of spaces in second param below should correspond
        # to indent in format_field() and format_content()
        return string.replace('\n', '\n            ')

    def format_field(obj, field):
        if not getattr(obj, field):
            return ''

        return textwrap.dedent('''\
            ///// %(model)s.%(id)i.%(field)s ORIGINAL
            %(value)s

            ///// %(model)s.%(id)i.%(field)s TRANSLATION
            %(value)s



            ''' % {
            'model': obj._meta.model_name,
            'id': obj.id,
            'field': field,
            'value': indent(getattr(obj, field)),
        })

    def format_content(obj, index, field, *fields, **kwargs):
        if not kwargs.get('value', '') and not obj.data[index].get(field):
            return ''

        return textwrap.dedent('''\
            ///// %(model)s.%(id)i.%(index)i.%(fields)s ORIGINAL
            %(value)s

            ///// %(model)s.%(id)i.%(index)i.%(fields)s TRANSLATION
            %(value)s



            ''' % {
            'model': obj._meta.model_name,
            'id': obj.id,
            'index': index,
            'fields': '.'.join([field] + list(fields)),
            'value': indent(kwargs.get('value', '')) or indent(obj.data[index].get(field)),
        })

    data = ''
    for program in queryset.order_by('id'):

        data += format_field(program, 'title')
        data += format_field(program, 'display_title')
        data += format_field(program, 'admin_note')

        for session in program.session_set.order_by('id'):

            data += format_field(session, 'title')
            data += format_field(session, 'display_title')
            data += format_field(session, 'admin_note')

            for content in session.content.order_by('id'):
                for index, pagelet in enumerate(content.data):

                    if pagelet['content_type'] == 'text':
                        data += format_content(content, index, 'content')

                    if pagelet['content_type'] == 'toggle':
                        data += format_content(content, index, 'content')
                        data += format_content(content, index, 'toggle')

                    if pagelet['content_type'] in ['toggleset', 'togglesetmulti']:
                        data += format_content(content, index, 'content', 'label', value=pagelet['content']['label'])

                        for i, item in enumerate(pagelet['content']['alternatives']):
                            data += format_content(content, index, 'content', 'alternatives', str(i), 'label', value=item['label'])

                    if pagelet['content_type'] == 'conditionalset':
                        for i, item in enumerate(pagelet['content']):
                            data += format_content(content, index, 'content', str(i), 'content', value=item['content'])

                    if pagelet['content_type'] == 'form':
                        for i, item in enumerate(pagelet['content']):

                            if item['field_type'] in ['numeric', 'string', 'textarea']:
                                data += format_content(content, index, 'content', str(i), 'label', value=item['label'])

                            if item['field_type'] == 'multiplechoice':
                                for j, alt in enumerate(item['alternatives']):
                                    data += format_content(content, index, 'content', str(i), 'alternatives', str(j), 'label', value=alt['label'])

                            if item['field_type'] == 'multipleselection':
                                for j, alt in enumerate(item['alternatives']):
                                    data += format_content(content, index, 'content', str(i), 'alternatives', str(j), 'label', value=alt['label'])

                    if pagelet['content_type'] == 'quiz':
                        for i, item in enumerate(pagelet['content']):
                            data += format_content(content, index, 'content', str(i), 'question', value=item['question'])
                            data += format_content(content, index, 'content', str(i), 'right', value=item['right'])
                            data += format_content(content, index, 'content', str(i), 'wrong', value=item['wrong'])

                            for j, alt in enumerate(item['alternatives']):
                                data += format_content(content, index, 'content', str(i), 'alternatives', str(j), 'label', value=alt['label'])

        for variable in program.variable_set.order_by('id'):
            data += format_field(variable, 'name')
            data += format_field(variable, 'display_name')
            data += format_field(variable, 'admin_note')
            data += format_field(variable, 'value')
            data += format_field(variable, 'random_set')

    response = HttpResponse(data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=text_content.md'

    return response


@staff_member_required
def import_text(request):
    '''
    Finds all TRANSLATION sections from a text file as exported by export_text(),
    extracts models, ids and field identifiers, and updates the given text.
    '''

    def drilldown_assign(obj, keys, value):
        '''
        Recursively drills down through a nested data structure by a
        given list of keys or list indices, and sets a value, leaving the
        data structure otherwise intact
        '''
        if not keys:
            obj = value
        else:
            try:
                keys[0] = int(keys[0])
            except:
                pass
            obj[keys[0]] = drilldown_assign(obj[keys[0]], keys[1:], value)
        return obj

    redirect = request.GET.get('next')

    if request.method == 'POST':

        text = request.FILES.get('text')

        matches = re.findall(
            '///// (\w+).(\d+).([\w\d.]+) TRANSLATION\n(.+?)\n\n\n',
            text.read(),
            re.DOTALL | re.UNICODE
        )

        for model, obj_id, identifier, value in matches:

            ct = ContentType.objects.get(app_label='system', model=model)
            obj = ct.get_object_for_this_type(id=obj_id)

            keys = identifier.split('.')

            update_kwargs = {}

            if len(keys) == 1:
                update_kwargs[identifier] = value

            elif len(keys) > 1:
                drilldown_assign(obj.data, keys, value)
                update_kwargs['data'] = obj.data

            # update database
            type(obj).objects.filter(id=obj_id).update(**update_kwargs)

        return HttpResponseRedirect(redirect)

    return render(request, 'import_text.html', {})


class VariableViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer


class VariableSearchViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    filter_backends = [VariableSearchFilter]
    search_fields = ["name", "display_name"]

    def get_queryset(self):
        """
        Should only return variables for the currently working
        program if any.
        """
        queryset = super(VariableSearchViewSet, self).get_queryset()
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Add system variables to search results
        """
        response = super(VariableSearchViewSet, self).list(request, *args, **kwargs)
        reserved_variables = [v for v in getattr(settings, "RESERVED_VARIABLES", {})
                              if "domains" in v and "user" in v["domains"]]
        response.data.extend(reserved_variables)
        return response


class ExpressionViewSet(CreateModelMixin, viewsets.ViewSet):
    """
    API resource for evaluating expressions.
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = ExpressionSerializer

    def get_serializer_context(self):
        return {
            'request': self.request,
            'format': self.format_kwarg,
            'view': self
        }

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.serializer_class
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)
