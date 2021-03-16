# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('domain', models.CharField(max_length=32, verbose_name='domain')),
                ('action', models.CharField(max_length=255, verbose_name='action', blank=True)),
                ('task_id', models.CharField(max_length=255, verbose_name='task')),
                ('time', models.DateTimeField(verbose_name='time')),
                ('content_type', models.ForeignKey(verbose_name='sender', to='contenttypes.ContentType',
                                                   on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'task',
                'verbose_name_plural': 'tasks',
            },
            bases=(models.Model,),
        ),
    ]
