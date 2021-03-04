# Generated by Django 2.2.17 on 2021-03-04 21:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_orderable_authors'),
        ('people', '0027_person_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='posts',
            field=models.ManyToManyField(through='blog.Author', to='blog.BlogPost'),
        ),
    ]
