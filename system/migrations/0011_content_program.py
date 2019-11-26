# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0010_migrate_conditions'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='program',
            field=models.ForeignKey(blank=True, to='system.Program',
                                    help_text='Optionally related to a specific program',
                                    null=True, verbose_name='program', on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
