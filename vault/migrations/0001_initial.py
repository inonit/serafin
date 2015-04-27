# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VaultUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254, verbose_name='e-mail address', blank=True)),
                ('phone', models.CharField(max_length=32, verbose_name='phone number', blank=True)),
            ],
            options={
                'verbose_name': 'vault user',
                'verbose_name_plural': 'vault users',
            },
            bases=(models.Model,),
        ),
    ]
