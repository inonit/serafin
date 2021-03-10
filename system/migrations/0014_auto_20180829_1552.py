# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        ('system', '0013_auto_20160428_0018'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='site',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='sites.Site', verbose_name='site'),
        ),
        migrations.AddField(
            model_name='program',
            name='style',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='stylesheet', choices=[(b'css/style.css', 'Default stylesheet'), (b'css/style-nalokson.css', 'Nalokson'), (b'css/style-miksmaster.css', 'Miksmaster'), (b'css/style-miksmaster-alt.css', 'Miksmaster alternate')]),
        ),
    ]
