from springkit.blocks.cta import CTAButtonsBlock
from wagtail import blocks

from .image_block import ImageBlock


class FeatureBlock(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/feature_block.html"
        label = "Feature"
        icon = "pick"
        group = "Body copy components"

    heading = blocks.CharBlock(
        required=True,
        max_length=80,
    )
    feature_text = blocks.RichTextBlock(
        max_length=400,
        features=[
            "bold",
            "document-link",
            "italic",
            "link",
            "ol",
            "ul",
        ],
    )
    image = ImageBlock()
    cta_buttons = CTAButtonsBlock(
        min_num=0,
        max_num=2,
        required=False,
    )
