# Generated by Django 2.2 on 2019-11-04 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0013_auto_20191104_1410'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='backdrop_path',
            field=models.CharField(default='', max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='overview',
            field=models.CharField(default='', max_length=5120, null=True),
        ),
        migrations.AlterField(
            model_name='film',
            name='poster_path',
            field=models.CharField(default='', max_length=100, null=True),
        ),
    ]
