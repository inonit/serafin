# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0012_auto_20150610_1723'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='content',
            field=models.ManyToManyField(to='system.Content', verbose_name='content', blank=True),
        ),
    ]
