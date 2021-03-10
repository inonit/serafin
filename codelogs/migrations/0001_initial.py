# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0016_code'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID',
                                        serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('time', models.DateTimeField(verbose_name='time')),
                ('code', models.ForeignKey(verbose_name='code',
                                           to='system.Code', on_delete=models.CASCADE)),
                ('content_type', models.ForeignKey(
                    verbose_name='sender', to='contenttypes.ContentType', on_delete=models.CASCADE)),
                ('subject', models.ForeignKey(verbose_name='subject',
                                              blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
            ],
            options={
                'verbose_name': 'codelog',
                'verbose_name_plural': 'codelogs',
            },
        ),
    ]
