# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0006_session_route_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='is_open',
            field=models.BooleanField(default=False, verbose_name='is open'),
            preserve_default=True,
        ),
    ]
