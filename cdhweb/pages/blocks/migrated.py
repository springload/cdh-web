from wagtail import blocks


class MigratedBlock(blocks.RichTextBlock):
    #: used to hold content migrated from mezzanine via a "kitchen-sink"
    #: approach; enable all supported wagtail features.
    #: Should NOT be used when creating new pages.

    class Meta:
        icon = "warning"
        template = "text-content.html"
        group = "Deprecated"

    def __init__(self, *args, **kwargs):
        kwargs["features"] = [
            "h3",
            "h4",
            "bold",
            "italic",
            "link",
            "ol",
            "ul",
            "hr",
            "blockquote",
            "superscript",
            "subscript",
            "strikethrough",
            "code",
            "image",
            "embed",
        ]
        super().__init__(*args, **kwargs)
