# Generated by Django 5.0.5 on 2024-06-05 03:16

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0013_remove_eventslandingpage_attachments_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="eventslandingpage",
            name="hero_image",
        ),
    ]