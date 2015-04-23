# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0008_variable_program'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='content',
            name='vars_used',
        ),
        migrations.RemoveField(
            model_name='session',
            name='vars_used',
        ),
        migrations.AlterField(
            model_name='session',
            name='route_slug',
            field=models.CharField(default=None, max_length=64, unique=True, null=True, verbose_name='route slug'),
            preserve_default=True,
        ),
    ]
