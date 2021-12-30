# Generated by Django 2.2.24 on 2021-12-22 14:39

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tournaments', '0004_tournament_tournament_format_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='players',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
    ]