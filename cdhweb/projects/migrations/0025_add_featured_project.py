# Generated by Django 5.0.6 on 2024-06-24 01:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0024_add_project_method_and_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectslandingpage',
            name='featured_project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='projects.project'),
        ),
    ]
