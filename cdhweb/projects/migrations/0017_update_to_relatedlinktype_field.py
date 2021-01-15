from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_project_member_to_person'),
        ('cdhpages', '0002_relatedlinktype')
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='resources',
            field=models.ManyToManyField(through='projects.ProjectResource', to='cdhpages.RelatedLinkType'),
        ),
        migrations.AlterField(
            model_name='ProjectResource',
            name='resource_type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='cdhpages.RelatedLinkType')
        )
    ]
