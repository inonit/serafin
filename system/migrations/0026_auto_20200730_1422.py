# Generated by Django 2.2 on 2020-07-30 11:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import filer.fields.image


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.FILER_IMAGE_MODEL),
        ('system', '0025_note'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='about',
            field=models.TextField(blank=True, null=True, verbose_name='about'),
        ),
        migrations.AddField(
            model_name='program',
            name='cover_image',
            field=filer.fields.image.FilerImageField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='program_cover_images', to=settings.FILER_IMAGE_MODEL, verbose_name='cover image'),
        ),
    ]
