# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-04-23 06:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('vincent', '0004_phonenumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 4, 23, 6, 46, 42, 88518, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
