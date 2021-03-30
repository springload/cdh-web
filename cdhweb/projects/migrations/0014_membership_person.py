# Generated by Django 2.2.17 on 2020-12-22 20:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0011_populate_nonproxy_person'),
        ('projects', '0013_unproxy_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='person',
            new_name="user"
        ),
        migrations.AddField(
            model_name='membership',
            name='person',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='people.Person'),
        ),
    ]
