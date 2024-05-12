# Generated by Django 5.0.5 on 2024-05-08 22:53

import django.db.models.deletion
import modelcluster.fields
import wagtail.blocks
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("cdhpages", "0004_homepage_hero_image_homepage_summary_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Footer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Footer",
                "verbose_name_plural": "Footer",
            },
        ),
        migrations.CreateModel(
            name="Level1MenuItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                (
                    "title",
                    models.CharField(max_length=60, verbose_name="Menu item title"),
                ),
                (
                    "overview",
                    models.TextField(max_length=120, verbose_name="Section overview"),
                ),
                (
                    "section_link_title",
                    models.CharField(max_length=60, verbose_name="Section link title"),
                ),
                (
                    "section_link",
                    wagtail.fields.StreamField(
                        [
                            ("page", wagtail.blocks.PageChooserBlock()),
                            ("external", wagtail.blocks.URLBlock()),
                        ],
                        use_json_field=True,
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="PrimaryNavigation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Primary Navigation",
                "verbose_name_plural": "Primary Navigation",
            },
        ),
        migrations.CreateModel(
            name="SecondaryNavigation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
            ],
            options={
                "verbose_name": "Secondary Navigation",
                "verbose_name_plural": "Secondary Navigation",
            },
        ),
        migrations.CreateModel(
            name="FooterColumn",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=255,
                        verbose_name="Column heading",
                    ),
                ),
                (
                    "footer",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="footer_columns",
                        to="cdhpages.footer",
                    ),
                ),
            ],
            options={
                "verbose_name": "Footer column",
                "verbose_name_plural": "Footer columns",
            },
        ),
        migrations.CreateModel(
            name="ColumnItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("body", wagtail.fields.RichTextField()),
                (
                    "column",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="column_items",
                        to="cdhpages.footercolumn",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ImprintLinkItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("title", models.CharField(max_length=60, verbose_name="Menu title")),
                (
                    "link",
                    wagtail.fields.StreamField(
                        [
                            ("page", wagtail.blocks.PageChooserBlock()),
                            ("external", wagtail.blocks.URLBlock()),
                        ],
                        use_json_field=True,
                    ),
                ),
                (
                    "imprint_link",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="imprint_links",
                        to="cdhpages.footer",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="Level2MenuItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("title", models.CharField(max_length=60, verbose_name="Item title")),
                (
                    "link",
                    wagtail.fields.StreamField(
                        [
                            ("page", wagtail.blocks.PageChooserBlock()),
                            ("external", wagtail.blocks.URLBlock()),
                        ],
                        use_json_field=True,
                    ),
                ),
                (
                    "l1_parent",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="l2_items",
                        to="cdhpages.level1menuitem",
                    ),
                ),
            ],
            options={
                "ordering": ["sort_order"],
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="level1menuitem",
            name="main_menu",
            field=modelcluster.fields.ParentalKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="l1_items",
                to="cdhpages.primarynavigation",
            ),
        ),
        migrations.CreateModel(
            name="SecondaryNavigationItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "sort_order",
                    models.IntegerField(blank=True, editable=False, null=True),
                ),
                ("title", models.CharField(max_length=60, verbose_name="Menu title")),
                (
                    "link",
                    wagtail.fields.StreamField(
                        [
                            ("page", wagtail.blocks.PageChooserBlock()),
                            ("external", wagtail.blocks.URLBlock()),
                        ],
                        use_json_field=True,
                    ),
                ),
                (
                    "secondary_menu",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="cdhpages.secondarynavigation",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
    ]