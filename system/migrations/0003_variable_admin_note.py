# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0002_auto_20150213_2248'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='admin_note',
            field=models.TextField(verbose_name='admin note', blank=True),
            preserve_default=True,
        ),
    ]
