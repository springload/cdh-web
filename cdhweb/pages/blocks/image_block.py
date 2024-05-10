from wagtail import blocks


class ImageBlock(blocks.StructBlock):
    class Meta:
        template = "core/blocks/image_block.html"
        label = "Image Block"

    # image - required

    # caption - a short caption for the image max 180 chars - richtextfield

    # credit - richtextfield - a credit line or attribution for the image

    # alt text - textfield max 80 - text to display if the image can't be viewed


    ####### USE SPRINGKIT