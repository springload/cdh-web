from collections.abc import Iterable

from springkit.blocks import JumplinkableH2Block
from wagtail import blocks


class AccordionBlock(blocks.StructBlock):
    """
    A list of accordion items

    """

    class Meta:
        template = "cdhpages/blocks/accordion_block.html"
        label = "Accordion"
        icon = "cogs"
        group = "Body copy components"

    heading = JumplinkableH2Block(required=False)

    description = blocks.RichTextBlock(
        features=["bold", "italic", "link", "document-link"], required=False
    )

    accordion_items = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "heading",
                    blocks.CharBlock(
                        verbose_name="Accordion Title", required=True, max_length=80
                    ),
                ),
                (
                    "body",
                    blocks.RichTextBlock(
                        features=[
                            "bold",
                            "italic",
                            "link",
                            "ol",
                            "ul",
                            "document-link",
                            "h3",
                            "h4",
                        ],
                        help_text="Only use H3 if you have not set an overall heading for the accordion block."
                    ),
                ),
            ]
        )
    )
