# Generated by Django 2.1.7 on 2019-03-17 05:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0016_auto_20190317_1028'),
    ]

    operations = [
        migrations.AddField(
            model_name='unityobject',
            name='type',
            field=models.CharField(default='Texture2D', max_length=30),
            preserve_default=False,
        ),
    ]
