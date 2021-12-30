# Generated by Django 2.2.24 on 2021-12-24 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0001_initial'),
        ('tournaments', '0007_game_time_format'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='games',
            field=models.ManyToManyField(to='games.ChessGame'),
        ),
    ]