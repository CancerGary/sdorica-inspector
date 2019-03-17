# Generated by Django 2.1.7 on 2019-03-17 02:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_auto_20190316_2119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='unityobject',
            name='data_crc32',
        ),
        migrations.RemoveField(
            model_name='unityobject',
            name='db_crc32',
        ),
        migrations.AddField(
            model_name='unityobject',
            name='data_hash',
            field=models.CharField(default='0'*32, max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='unityobject',
            name='db_hash',
            field=models.CharField(db_index=True, default='0'*32, max_length=32),
            preserve_default=False,
        ),
    ]