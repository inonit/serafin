# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='post_value',
            field=models.CharField(max_length=1024, verbose_name='post value', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='event',
            name='pre_value',
            field=models.CharField(max_length=1024, verbose_name='pre value', blank=True),
            preserve_default=True,
        ),
    ]
