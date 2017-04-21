# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def merge_vault_values(apps, schema_editor):

    User = apps.get_model('users', 'User')
    VaultUser = apps.get_model('vault', 'VaultUser')

    for user in User.objects.all():
        try:
            vault_user = VaultUser.objects.get(id=user.id)
        except:
            continue

        user.email = vault_user.email
        user.phone = vault_user.phone
        user.save()


def unmerge_vault_values(apps, schema_editor):

    pass


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_add_vault_fields'),
        ('vault', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(merge_vault_values, reverse_code=unmerge_vault_values),
    ]
