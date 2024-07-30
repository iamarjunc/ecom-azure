# Generated by Django 5.0.6 on 2024-06-29 02:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_ordereditem_total'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ordereditem',
            name='total',
        ),
        migrations.AddField(
            model_name='order',
            name='total',
            field=models.FloatField(default=0),
        ),
    ]