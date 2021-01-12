
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resources', '0009_move_resourcetype_to_pages_app'),
        ('cdhpages', '0002_relatedlinktype')
    ]

    operations = [
        # Update other resource models with new location. This is will be temporary.
        migrations.AlterField(
            model_name='personresource',
            name='resource_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cdhpages.RelatedLinkType'),
        )
    ]
