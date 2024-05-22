from wagtail import blocks
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock


class TableBlock(blocks.StructBlock):
    """
    CMS controlled Simple Table block
    """

    class Meta:
        template = "cdhpages/blocks/table_block.html"
        label = "Simple Table"
        icon = "table"
        group = "Body copy components"

    caption = blocks.CharBlock(
        help_text="Table caption",
        label="Caption",
        required=False,
    )

    notes = blocks.RichTextBlock(
        features=["bold", "italic", "link", "document-link"],
        required=False,
        help_text=("Primarily for using for footnotes from cells with asterisks"),
        label="Table notes",
    )

    table = TypedTableBlock(
        [
            (
                "rich_text",
                blocks.RichTextBlock(
                    features=[
                        "bold",
                        "italic",
                        "link",
                        "ol",
                        "ul",
                        "h3",
                    ]
                ),
            ),
        ],
        help_text="It is recommended to use a minimal number of columns, to ensure the table is usable on mobile and desktop.",
        max_num=1,
        min_num=1,
    )
