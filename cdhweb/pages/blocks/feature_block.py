from wagtail import blocks


class FeatureBlock(blocks.StructBlock):
    class Meta:
        template = "core/blocks/feature_block.html"
        label = "Feature Block"

    # heading - charfield

    # feature text - richtextfield max 400 chars

    # image

    # primary cta button

    # secondary cta button

    #### USE SPRINGKIT