# Generated by Django 2.1.5 on 2019-01-29 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20190128_0003'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvertRule',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern', models.CharField(max_length=100)),
                ('text', models.TextField(null=True)),
            ],
        ),
        migrations.DeleteModel(
            name='TranslateTable',
        ),
    ]