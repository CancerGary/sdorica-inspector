# Generated by Django 2.1.4 on 2018-12-24 16:14

import backend.api.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_imperium_md5'),
    ]

    operations = [
        migrations.AddField(
            model_name='imperium',
            name='uuid',
            field=models.UUIDField(null=True),
        ),
        migrations.AlterField(
            model_name='imperium',
            name='game_version',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='imperiums', to='api.GameVersion'),
        ),
        migrations.AlterField(
            model_name='imperium',
            name='type_id',
            field=models.IntegerField(choices=[(0, 'unknown'), (1, 'gamedata'), (2, 'android'), (3, 'androidExp'), (4, 'localization')], default=0),
        ),
    ]