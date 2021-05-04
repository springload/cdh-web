# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def create_exec_committee_positions(apps, schema_editor):
    # create exec committee Titlesif they do not already exist
    Title = apps.get_model('people', 'Title')
    Title.objects.get_or_create(title='Executive Committee Member', sort_order=10)
    Title.objects.get_or_create(title='Sits with Executive Committee', sort_order=11)


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_exec_committee_positions,
                             reverse_code=migrations.RunPython.noop),
    ]
