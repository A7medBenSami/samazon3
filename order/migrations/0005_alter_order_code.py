# Generated by Django 4.1.4 on 2022-12-22 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0004_remove_order_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='code',
            field=models.IntegerField(editable=False, unique=True),
        ),
    ]
