# Generated by Django 2.2 on 2019-11-04 13:14

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0004_auto_20191101_1529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='film',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]
