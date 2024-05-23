from springkit.blocks.cta import CTAButtonsBlock
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


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
    image = ImageChooserBlock(
        label="Image",
        required=True,
    )

    alt_text = blocks.CharBlock(
        help_text="Alternative text in case the image can't be displayed.",
        required=False,
        max_length=80,
    )
    cta_buttons = CTAButtonsBlock(
        min_num=0,
        max_num=2,
        required=False,
    )
