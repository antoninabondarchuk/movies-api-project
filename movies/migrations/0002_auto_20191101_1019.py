# Generated by Django 2.2 on 2019-11-01 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='source_id',
            field=models.IntegerField(default=None),
        ),
        migrations.AddField(
            model_name='genre',
            name='source_id',
            field=models.IntegerField(default=None),
        ),
    ]