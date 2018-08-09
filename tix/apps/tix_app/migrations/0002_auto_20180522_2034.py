# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-22 20:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tix_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='sale_status',
            field=models.CharField(choices=[(0, 'available'), (1, 'pending'), (2, 'sold')], default=0, max_length=1),
        ),
    ]
