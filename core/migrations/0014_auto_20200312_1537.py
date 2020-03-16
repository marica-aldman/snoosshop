# Generated by Django 2.2.6 on 2020-03-12 14:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20200312_1534'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='freight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Freight'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='freight_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
