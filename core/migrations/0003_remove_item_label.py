# Generated by Django 3.0 on 2020-02-17 12:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20200217_1321'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='label',
        ),
    ]
