# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-14 13:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0008_update_light_jobs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='runhistory',
            name='date',
            field=models.DateTimeField(),
        ),
    ]
