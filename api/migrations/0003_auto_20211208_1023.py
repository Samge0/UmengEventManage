# Generated by Django 3.2.8 on 2021-12-08 10:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_keyvalue'),
    ]

    operations = [
        migrations.CreateModel(
            name='UmEventModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('um_md5', models.CharField(max_length=128)),
                ('um_key', models.CharField(max_length=128)),
                ('um_eventId', models.CharField(max_length=128)),
                ('um_name', models.CharField(default='', max_length=128)),
                ('um_displayName', models.CharField(max_length=128)),
                ('um_status', models.CharField(max_length=10)),
                ('um_eventType', models.IntegerField(default=0)),
                ('um_countToday', models.IntegerField(default=0)),
                ('um_countYesterday', models.IntegerField(default=0)),
                ('um_deviceYesterday', models.IntegerField(default=0)),
                ('um_date', models.DateTimeField()),
            ],
        ),
        migrations.AlterField(
            model_name='keyvalue',
            name='kv_add_time',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='umkey',
            name='um_add_time',
            field=models.DateTimeField(),
        ),
    ]