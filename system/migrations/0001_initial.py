# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=64, verbose_name='title')),
                ('display_title', models.CharField(max_length=64, verbose_name='display title')),
                ('content_type', models.CharField(verbose_name='content type', max_length=32, editable=False)),
                ('admin_note', models.TextField(verbose_name='admin note', blank=True)),
                ('data', jsonfield.fields.JSONField(default='[]')),
            ],
            options={
                'verbose_name': 'content',
                'verbose_name_plural': 'contents',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Program',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=64, verbose_name='title')),
                ('display_title', models.CharField(max_length=64, verbose_name='display title')),
                ('admin_note', models.TextField(verbose_name='admin note', blank=True)),
            ],
            options={
                'verbose_name': 'program',
                'verbose_name_plural': 'programs',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProgramUserAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='start time')),
                ('time_factor', models.DecimalField(default=1.0, verbose_name='time factor', max_digits=5, decimal_places=3)),
                ('program', models.ForeignKey(verbose_name='program', to='system.Program', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'user access',
                'verbose_name_plural': 'user accesses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=64, verbose_name='title')),
                ('display_title', models.CharField(max_length=64, verbose_name='display title')),
                ('admin_note', models.TextField(verbose_name='admin note', blank=True)),
                ('start_time_delta', models.IntegerField(default=0, verbose_name='start time delta')),
                ('start_time_unit', models.CharField(default='hours', max_length=32, verbose_name='start time unit', choices=[('hours', 'hours'), ('days', 'days')])),
                ('end_time_delta', models.IntegerField(default=0, verbose_name='end time delta')),
                ('end_time_unit', models.CharField(default='hours', max_length=32, verbose_name='end time unit', choices=[('hours', 'hours'), ('days', 'days')])),
                ('start_time', models.DateTimeField(null=True, verbose_name='first start time', blank=True)),
                ('scheduled', models.BooleanField(default=False, verbose_name='scheduled')),
                ('trigger_login', models.BooleanField(default=True, verbose_name='trigger login')),
                ('data', jsonfield.fields.JSONField(default='undefined')),
                ('content', models.ManyToManyField(to='system.Content', null=True, verbose_name='content', blank=True)),
                ('program', models.ForeignKey(verbose_name='program', to='system.Program', on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'session',
                'verbose_name_plural': 'sessions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Variable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64, verbose_name='name')),
                ('display_name', models.CharField(default='', max_length=64, verbose_name='display name', blank=True)),
                ('value', models.CharField(default='', max_length=32, verbose_name='initial value', blank=True)),
                ('user_editable', models.BooleanField(default=False, verbose_name='user editable')),
                ('random_type', models.CharField(blank=True, max_length=16, null=True, verbose_name='randomization type', choices=[('boolean', 'boolean'), ('numeric', 'numeric'), ('string', 'string')])),
                ('randomize_once', models.BooleanField(default=False, verbose_name='randomize once')),
                ('range_min', models.IntegerField(null=True, verbose_name='range min (inclusive)', blank=True)),
                ('range_max', models.IntegerField(null=True, verbose_name='range max (inclusive)', blank=True)),
                ('random_set', models.TextField(verbose_name='random string set', blank=True)),
            ],
            options={
                'verbose_name': 'variable',
                'verbose_name_plural': 'variables',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='session',
            name='vars_used',
            field=models.ManyToManyField(to='system.Variable', editable=False),
            preserve_default=True,
        ),
    ]
