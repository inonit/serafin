# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


OPMAP = {
    'eq': '==',
    'ne': '!=',
    'lt': '<',
    'le': '<=',
    'gt': '>',
    'ge': '>=',
    'in': 'in',
}


def migrate_conditions(apps, schema_editor):

    def typecast(value):
        try:
            int(value)
        except:
            value = '"%s"' % value
        return value

    Session = apps.get_model('system', 'Session')

    for session in Session.objects.all():
        for edge in session.data.get('edges', []):

            expression = ' AND '.join([
                ' '.join([
                    '$%s' % condition.get('var_name') if condition.get('var_name') else '',
                    OPMAP.get(condition.get('operator'), ''),
                    typecast(condition.get('value')) if condition.get('value') else 'None'
                ])
                for condition in edge.get('conditions', [])
            ])

            if expression:
                edge['expression'] = expression

        Session.objects.filter(id=session.id).update(data=session.data)

    Page = apps.get_model('system', 'Page')

    for page in Page.objects.all():
        for pagelet in page.data:
            if pagelet.get('content_type') == 'conditionalset':

                for content in pagelet.get('content', []):

                    expression = ' AND '.join([
                        ' '.join([
                            '$%s' % condition.get('var_name') if condition.get('var_name') else '',
                            OPMAP.get(condition.get('operator'), ''),
                            typecast(condition.get('value')) if condition.get('value') else 'None'
                        ])
                        for condition in content.get('conditions', [])
                    ])

                    if expression:
                        content['expression'] = expression

        Page.objects.filter(id=page.id).update(data=page.data)


def delete_expressions(apps, schema_editor):

    Session = apps.get_model('system', 'Session')

    for session in Session.objects.all():
        for edge in session.data.get('edges', []):
            if edge.get('expression'):
                del edge['expression']

        Session.objects.filter(id=session.id).update(data=session.data)

    Page = apps.get_model('system', 'Page')

    for page in Page.objects.all():
        for pagelet in page.data:
            if pagelet.get('content_type') == 'conditionalset':

                for content in pagelet.get('content', []):
                    if content.get('expression'):
                        del content['expression']

        Page.objects.filter(id=page.id).update(data=page.data)


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0009_auto_20150423_0157'),
    ]

    operations = [
        migrations.RunPython(migrate_conditions, reverse_code=delete_expressions),
    ]
