# Generated by Django 4.2.3 on 2023-08-03 22:02

import wagtail.blocks
import wagtail.documents.blocks
import wagtail.embeds.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtail.snippets.blocks
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_exec_committee_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="attachments",
            field=wagtail.fields.StreamField(
                [
                    ("document", wagtail.documents.blocks.DocumentChooserBlock()),
                    (
                        "link",
                        wagtail.snippets.blocks.SnippetChooserBlock(
                            "cdhpages.ExternalAttachment"
                        ),
                    ),
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="profile",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "paragraph",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h2",
                                "h3",
                                "h4",
                                "bold",
                                "italic",
                                "link",
                                "ol",
                                "ul",
                                "hr",
                                "blockquote",
                                "document",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                            ]
                        ),
                    ),
                    (
                        "image",
                        wagtail.blocks.StructBlock(
                            [
                                ("image", wagtail.images.blocks.ImageChooserBlock()),
                                (
                                    "alternative_text",
                                    wagtail.blocks.TextBlock(
                                        help_text="Alternative text for visually impaired users to\nbriefly communicate the intended message of the image in this context.",
                                        required=True,
                                    ),
                                ),
                                (
                                    "caption",
                                    wagtail.blocks.RichTextBlock(
                                        features=[
                                            "bold",
                                            "italic",
                                            "link",
                                            "superscript",
                                        ],
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "svg_image",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "image",
                                    wagtail.documents.blocks.DocumentChooserBlock(),
                                ),
                                (
                                    "alternative_text",
                                    wagtail.blocks.TextBlock(
                                        help_text="Alternative text for visually impaired users to\nbriefly communicate the intended message of the image in this context.",
                                        required=True,
                                    ),
                                ),
                                (
                                    "caption",
                                    wagtail.blocks.RichTextBlock(
                                        features=[
                                            "bold",
                                            "italic",
                                            "link",
                                            "superscript",
                                        ],
                                        required=False,
                                    ),
                                ),
                                (
                                    "extended_description",
                                    wagtail.blocks.RichTextBlock(
                                        features=["p"],
                                        help_text="This text will only be read to     non-sighted users and should describe the major insights or     takeaways from the graphic. Multiple paragraphs are allowed.",
                                        required=False,
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "embed",
                        wagtail.embeds.blocks.EmbedBlock(
                            help_text='For e.g. videos on YouTube, use the value in the URL bar.\n    For other content, look for an "oEmbed URL" option. For videos from\n    Princeton\'s Media Central, "oEmbed URL" is in the "Share" menu.'
                        ),
                    ),
                    (
                        "migrated",
                        wagtail.blocks.RichTextBlock(
                            features=[
                                "h3",
                                "h4",
                                "bold",
                                "italic",
                                "link",
                                "ol",
                                "ul",
                                "hr",
                                "blockquote",
                                "document",
                                "superscript",
                                "subscript",
                                "strikethrough",
                                "code",
                                "image",
                                "embed",
                            ],
                            icon="warning",
                        ),
                    ),
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
    ]
