# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0013_auto_20160428_0018'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='program_restrictions',
            field=models.ManyToManyField(related_query_name='user_restriction', related_name='user_restriction_set',
                                         to='system.Program', blank=True,
                                         help_text='Staff user has limited access only to the chosen Programs (and related data). If no Programs are chosen, there is no restriction.',
                                         verbose_name='program restrictions'),
        ),
    ]
