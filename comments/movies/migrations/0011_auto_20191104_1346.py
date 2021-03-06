# Generated by Django 2.2 on 2019-11-04 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0010_auto_20191104_1340'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='adult',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='film',
            name='backdrop_path',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='film',
            name='original_language',
            field=models.CharField(default='en-US', max_length=5),
        ),
        migrations.AlterField(
            model_name='film',
            name='original_title',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='film',
            name='overview',
            field=models.CharField(default='', max_length=512),
        ),
        migrations.AlterField(
            model_name='film',
            name='popularity',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='film',
            name='poster_path',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='film',
            name='release_date',
            field=models.CharField(default='01-01-1970', max_length=50),
        ),
        migrations.AlterField(
            model_name='film',
            name='title',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='film',
            name='video',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='film',
            name='vote_average',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='film',
            name='vote_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='genre',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
    ]
