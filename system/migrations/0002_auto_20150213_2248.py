# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='programuseraccess',
            name='user',
            field=models.ForeignKey(verbose_name='user', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='program',
            name='users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='users', through='system.ProgramUserAccess'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='content',
            name='vars_used',
            field=models.ManyToManyField(to='system.Variable', editable=False),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
            ],
            options={
                'verbose_name': 'e-mail',
                'proxy': True,
                'verbose_name_plural': 'e-mails',
            },
            bases=('system.content',),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
            ],
            options={
                'verbose_name': 'page',
                'proxy': True,
                'verbose_name_plural': 'pages',
            },
            bases=('system.content',),
        ),
        migrations.CreateModel(
            name='SMS',
            fields=[
            ],
            options={
                'verbose_name': 'SMS',
                'proxy': True,
                'verbose_name_plural': 'SMSs',
            },
            bases=('system.content',),
        ),
    ]
