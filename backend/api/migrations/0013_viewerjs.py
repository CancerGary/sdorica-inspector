# Generated by Django 2.1.7 on 2019-02-23 13:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0012_auto_20190222_2313'),
    ]

    operations = [
        migrations.CreateModel(
            name='ViewerJS',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('javascript', models.TextField()),
                ('unity_type', models.CharField(max_length=40, unique=True)),
            ],
        ),
    ]