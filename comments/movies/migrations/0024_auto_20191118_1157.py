# Generated by Django 2.2 on 2019-11-18 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0023_auto_20191108_1420'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tv',
            name='source_id',
            field=models.IntegerField(null=True),
        ),
    ]
