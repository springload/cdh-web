from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    # Before altering the model, ensure that all other app migrations have referenced it
    dependencies = [
        ('resources', '0011_delete_resourcelinktype_model'),
        ('projects', '0019_inherit_from_relatedlink'),
        ('people', '0021_peoplelandingpage'),
        ('cdhpages', '0002_relatedlinktype')
    ]

    operations = [
        # Move PersonResource from resources app to people app and rename to PersonRelatedLink
        migrations.SeparateDatabaseAndState(
            database_operations=[migrations.AlterModelTable('PersonResource', 'people_personrelatedlink')],
            state_operations=[migrations.DeleteModel('PersonResource')]
        )
    ]
