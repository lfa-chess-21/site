# Generated by Django 2.2.24 on 2021-12-20 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tournaments', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='end',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='is_open',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='start',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='subscribe_date',
        ),
    ]
