# Generated by Django 5.0.5 on 2024-07-05 01:30

import wagtail.documents.blocks
import wagtail.fields
import wagtail.snippets.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_alter_project_accordion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='attachments',
            field=wagtail.fields.StreamField([('document', wagtail.documents.blocks.DocumentChooserBlock()), ('link', wagtail.snippets.blocks.SnippetChooserBlock('cdhpages.ExternalAttachment'))], blank=True, help_text='This block exists to help with data migration. It will be deleted when content loading is complete.', use_json_field=True),
        ),
    ]
