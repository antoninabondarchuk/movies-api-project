# Generated by Django 2.2 on 2019-11-04 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0011_auto_20191104_1346'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='overview',
            field=models.CharField(default='', max_length=5120),
        ),
    ]