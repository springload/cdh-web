# Generated by Django 5.0.6 on 2024-06-23 22:56

import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_alter_project_body'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='tags',
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=wagtail.fields.RichTextField(blank=True, help_text='Short introduction to the page, aim for max two clear sentences (max. 200 chars).\n        Used to orient the user and help them identify relevancy of the page to meet their needs. ', max_length=200, null=True, verbose_name='Page Summary'),
        ),
        migrations.AlterField(
            model_name='projectslandingpage',
            name='description',
            field=wagtail.fields.RichTextField(blank=True, help_text='Short introduction to the page, aim for max two clear sentences (max. 200 chars).\n        Used to orient the user and help them identify relevancy of the page to meet their needs. ', max_length=200, null=True, verbose_name='Page Summary'),
        ),
        migrations.DeleteModel(
            name='ProjectTag',
        ),
    ]
