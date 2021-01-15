from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cdhpages', '0002_relatedlinktype'),
        ('people', '0021_peoplelandingpage'),
        ('resources', '0012_move_personresource_to_people_app')
    ]

    state_operations = [
        migrations.CreateModel(
            name='PersonRelatedLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField()),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.Person')),
                ('resource_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdhpages.RelatedLinkType')),
            ],
        ),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(state_operations=state_operations)
    ]