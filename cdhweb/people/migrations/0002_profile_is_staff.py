# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-14 17:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_staff',
            field=models.BooleanField(default=False, help_text='If checked, this person will be listed on the CDH staff page.')
        ),
    ]