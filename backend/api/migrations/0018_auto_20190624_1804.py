# Generated by Django 2.1.8 on 2019-06-24 10:04

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0017_unityobject_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imperium',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
