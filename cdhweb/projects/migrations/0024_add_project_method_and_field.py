# Generated by Django 5.0.6 on 2024-06-24 01:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_remove_project_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='ProjectMethod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='project',
            name='field',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='projects.projectfield'),
        ),
        migrations.AddField(
            model_name='project',
            name='method',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='projects', to='projects.projectmethod'),
        ),
    ]