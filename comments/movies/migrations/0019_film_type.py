# Generated by Django 2.2 on 2019-11-05 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0018_auto_20191104_1652'),
    ]

    operations = [
        migrations.AddField(
            model_name='film',
            name='type',
            field=models.CharField(default='movie', max_length=5, null=True),
        ),
    ]