# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0011_content_program'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='data',
            field=jsonfield.fields.JSONField(default=[]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='content',
            name='program',
            field=models.ForeignKey(blank=True, to='system.Program',
                                    help_text='Can optionally be bound to a specific program',
                                    null=True, verbose_name='program', on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='session',
            name='data',
            field=jsonfield.fields.JSONField(default='{"nodes": [], "edges": []}'),
            preserve_default=True,
        ),
    ]
