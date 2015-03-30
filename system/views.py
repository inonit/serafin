# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

import textwrap

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from rest_framework import viewsets

from .models import Variable, Program, Session, Page, Email, SMS
from .serializers import VariableSerializer
from .filters import VariableSearchFilter

@staff_member_required
def export_text(request):

    ct_id = request.GET.get('ct')
    ct = ContentType.objects.get_for_id(id=ct_id)

    ids = request.GET.get('ids').split(',')
    queryset = ct.get_all_objects_for_this_type(id__in=ids)

    def indent(string):
        # Number of spaces in second param below should correspond
        # to indent in format_field() and format_content()
        return string.replace('\n', '\n            ')

    def format_field(obj, field):
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
    variables = []
    for program in queryset.order_by('id'):

        data += format_field(program, 'title')
        data += format_field(program, 'display_title')
        data += format_field(program, 'admin_note')

        for session in program.session_set.order_by('id'):

            data += format_field(session, 'title')
            data += format_field(session, 'display_title')
            data += format_field(session, 'admin_note')

            for variable in session.vars_used.order_by('id'):
                variables.append(variable)

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


    response = HttpResponse(data, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename=text_content.md'

    return response


@staff_member_required
def import_text(request):

    redirect = request.GET.get('next')
    text = request.POST.get('text')

    if request.method == 'POST':

        return HttpResponseRedirect(redirect)


    context = {
        'text': text
    }

    return render(request, 'import_text.html', context)






class VariableViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer


class VariableSearchViewSet(viewsets.ModelViewSet):

    queryset = Variable.objects.all()
    serializer_class = VariableSerializer
    filter_backends = [VariableSearchFilter]
    search_fields = ["name", "display_name"]


