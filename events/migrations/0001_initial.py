# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='time')),
                ('domain', models.CharField(max_length=32, verbose_name='domain')),
                ('variable', models.CharField(max_length=64, verbose_name='variable')),
                ('pre_value', models.CharField(max_length=64, verbose_name='pre value', blank=True)),
                ('post_value', models.CharField(max_length=64, verbose_name='post value', blank=True)),
                ('actor', models.ForeignKey(verbose_name='actor', to=settings.AUTH_USER_MODEL,
                                            on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
            },
            bases=(models.Model,),
        ),
    ]
