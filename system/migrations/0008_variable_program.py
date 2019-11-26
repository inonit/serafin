# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def assign_program(apps, schema_editor):

    Program = apps.get_model('system', 'Program')

    for program in Program.objects.all():
        for session in program.session_set.all():
            for variable in session.vars_used.all():
                variable.program = program
                variable.save()
            for content in session.content.all():
                for variable in content.vars_used.all():
                    variable.program = program
                    variable.save()


class Migration(migrations.Migration):

    dependencies = [
        ('system', '0007_session_is_open'),
    ]

    operations = [
        migrations.AddField(
            model_name='variable',
            name='program',
            field=models.ForeignKey(verbose_name='program', to='system.Program', null=True, on_delete=models.CASCADE),
            preserve_default=True,
        ),
        migrations.RunPython(assign_program),
    ]
