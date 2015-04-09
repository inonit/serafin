# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_admin_visitor(apps, schema_editor):

    Group = apps.get_model('auth', 'Group')
    group, created = Group.objects.get_or_create(name='Admin visitor')

    Permission = apps.get_model('auth', 'Permission')
    for permission in Permission.objects.all():
        if 'change' in permission.codename:
            group.permissions.add(permission)


def remove_admin_visitor(apps, schema_editor):

    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(name='Admin visitor').delete()


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0003_variable_admin_note'),
    ]

    operations = [
        migrations.RunPython(add_admin_visitor, reverse_code=remove_admin_visitor),
    ]
