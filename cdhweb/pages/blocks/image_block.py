from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class ImageBlock(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/image_block.html"
        label = "Image"
        icon = "image"
        group = "Images and media"

    image = ImageChooserBlock(
        label="Image",
        required=True,
    )

    caption = blocks.RichTextBlock(
        features=[
            "italic",
            "bold",
            "link",
        ],
        help_text="A short caption for the image.",
        required=False,
        max_length=180,
    )

    credit = blocks.RichTextBlock(
        features=[
            "italic",
            "bold",
            "link",
        ],
        help_text="A credit line or attribution for the image.",
        required=False,
        max_length=80,
    )

    alt_text = blocks.CharBlock(
        help_text="Alternative text in case the image can't be displayed.",
        required=False,
        max_length=80,
    )
