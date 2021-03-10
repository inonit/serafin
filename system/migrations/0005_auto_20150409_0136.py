# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0004_auto_20150409_0055'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='variable',
            options={'ordering': ('display_name', 'name', 'value'), 'verbose_name': 'variable', 'verbose_name_plural': 'variables'},
        ),
    ]
