from wagtail import blocks


class RichTextBlock(blocks.RichTextBlock):
    """
    Standard rich text block
    """

    class Meta:
        icon = "pilcrow"
        template = "cdhpages/blocks/rich_text.html"

    def __init__(self, *args, **kwargs):
        kwargs["features"] = [
            "ul",
            "ol",
            "italic",
            "bold",
            "h3",
            "h4",
            "h5",
            "link",
            "blockquote",
        ]
        super().__init__(*args, **kwargs)
