# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0005_auto_20150409_0136'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='route_slug',
            field=models.CharField(max_length=64, unique=True, null=True, verbose_name='route slug'),
            preserve_default=True,
        ),
    ]
