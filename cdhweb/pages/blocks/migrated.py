from wagtail import blocks


class MigratedBlock(blocks.RichTextBlock):
    class Meta:
        group = "Deprecated"
        icon = "warning"

    #: used to hold content migrated from mezzanine via a "kitchen-sink"
    #: approach; enable all supported wagtail features.
    #: Should NOT be used when creating new pages.
    migrated = blocks.RichTextBlock(
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
            "superscript",
            "subscript",
            "strikethrough",
            "code",
            "image",
            "embed",
        ],
        icon="warning",
        template="text-content.html",
    )
