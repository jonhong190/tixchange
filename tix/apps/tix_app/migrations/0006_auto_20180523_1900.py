# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-05-23 19:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tix_app', '0005_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='ticket',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='ticket_photos', to='tix_app.Ticket'),
        ),
        migrations.AddField(
            model_name='photo',
            name='user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='photo_uploads', to='tix_app.User'),
        ),
    ]
