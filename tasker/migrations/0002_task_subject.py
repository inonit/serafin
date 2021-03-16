# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tasker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='subject',
            field=models.ForeignKey(verbose_name='subject', blank=True, to=settings.AUTH_USER_MODEL, null=True,
                                    on_delete=models.CASCADE),
            preserve_default=True,
        ),
    ]
