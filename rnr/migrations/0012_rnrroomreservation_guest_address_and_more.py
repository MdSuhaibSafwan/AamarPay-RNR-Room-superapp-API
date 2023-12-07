# Generated by Django 4.2.4 on 2023-12-07 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rnr', '0011_rnrroomreservation_rooms'),
    ]

    operations = [
        migrations.AddField(
            model_name='rnrroomreservation',
            name='guest_address',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='rnrroomreservation',
            name='guest_email',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='rnrroomreservation',
            name='guest_mobile_no',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='rnrroomreservation',
            name='guest_name',
            field=models.CharField(max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='rnrroomreservation',
            name='guest_special_request',
            field=models.CharField(max_length=500, null=True),
        ),
    ]