# Generated by Django 4.2.4 on 2023-08-24 10:24

from django.db import migrations, models
import rnr.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RNRAccessToken',
            fields=[
                ('id', models.UUIDField(default=rnr.models.uuid_without_dash, editable=False, primary_key=True, serialize=False, unique=True)),
                ('token', models.CharField(max_length=300, unique=True)),
                ('token_type', models.CharField(max_length=100, null=True)),
                ('expired', models.BooleanField(default=False)),
                ('expire_time', models.FloatField(default=3500.0)),
                ('created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]