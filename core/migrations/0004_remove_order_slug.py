# Generated by Django 2.2.6 on 2020-03-05 16:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20200305_1647'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='slug',
        ),
    ]
