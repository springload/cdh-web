from wagtail import blocks


class BodyCopy(blocks.StructBlock):
    class Meta:
        template = "core/blocks/body_copy.html"
        label = "Body Copy"

    # body - add a block of text to a page. Rich text with blocks