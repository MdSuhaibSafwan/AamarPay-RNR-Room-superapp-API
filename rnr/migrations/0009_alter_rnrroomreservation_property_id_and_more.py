# Generated by Django 4.2.4 on 2023-10-17 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rnr', '0008_rnrroomreservation_mer_txid_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rnrroomreservation',
            name='property_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='rnrroomreservation',
            name='reservation_id',
            field=models.BigIntegerField(),
        ),
    ]
