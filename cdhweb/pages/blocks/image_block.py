from django.db import models
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class UnsizedImageBlock(blocks.StructBlock):
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
        help_text="Describe the image for screen readers",
        required=False,
        max_length=80,
    )


class ImageBlock(UnsizedImageBlock):
    """ImageBlock - with size option"""

    class ImageSizeOption(models.TextChoices):
        SMALL = "small", "small"
        MEDIUM = "medium", "medium"
        LARGE = "large", "large"

    size = blocks.ChoiceBlock(
        choices=ImageSizeOption.choices,
        default=ImageSizeOption.MEDIUM,
        required=True,
        label="Image Size",
    )
