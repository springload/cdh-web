from wagtail import blocks


class CTABlock(blocks.StructBlock):
    class Meta:
        template = "core/blocks/cta.html"
        label = "Call to action"
        icon = "arrow-right-full"

    heading = blocks.CharBlock(max_length=80, required=True)
    introduction = blocks.TextBlock(
        max_length=150, required=False, help_text="Max 150 characters"
    )

    primary_link_text = blocks.CharBlock(max_length=40, required=True)

    secondary_link_text = blocks.CharBlock(max_length=40, required=False)
