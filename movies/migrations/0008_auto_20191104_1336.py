# Generated by Django 2.2 on 2019-11-04 13:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0007_auto_20191104_1319'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False),
        ),
    ]