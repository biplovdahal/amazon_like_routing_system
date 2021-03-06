# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2018-04-15 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('latitude', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('longitude', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('city', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('state', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('country', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('address', models.CharField(blank=True, default=None, max_length=120, null=True)),
                ('zipcode', models.CharField(blank=True, default=None, max_length=120, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='omniapi.Location')),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('miles_from_warehouse', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Van',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('driver_first_name', models.CharField(blank=True, default=None, max_length=120, null=True, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='route',
            name='van',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='omniapi.Van'),
        ),
        migrations.AddField(
            model_name='order',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='omniapi.Route'),
        ),
    ]
