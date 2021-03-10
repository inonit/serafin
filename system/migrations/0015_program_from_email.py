# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0014_auto_20180829_1552'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='from_email',
            field=models.CharField(max_length=128, null=True, verbose_name='from email', blank=True),
        ),
    ]
