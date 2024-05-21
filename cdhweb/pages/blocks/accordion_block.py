from collections.abc import Iterable

from wagtail import blocks


class AccordionBlock(blocks.StructBlock):
    """
    A list of accordion items

    """

    class Meta:
        template = "cdhpages/blocks/accordion_block.html"
        label = "Accordion"
        icon = "cogs"

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
                        ]
                    ),
                ),
            ]
        )
    )
