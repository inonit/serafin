# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0015_program_from_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='Code',
            fields=[
            ],
            options={
                'verbose_name': 'code',
                'proxy': True,
                'verbose_name_plural': 'codes',
            },
            bases=('system.content',),
        ),
    ]
