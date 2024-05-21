from wagtail import blocks


class Note(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/note.html"
        label = "Note"
        icon = "clipboard-list"
        group = "Body copy components"

    heading = blocks.TextBlock(
        required=False,
        help_text=("Optional heading"),
    )

    message = blocks.RichTextBlock(
        features=["bold", "italic", "link", "ul", "ol"],
        help_text="Note message up to 750 chars",
        required=True,
        max_length=750,
    )
