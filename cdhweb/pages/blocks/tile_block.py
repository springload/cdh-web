from django.db import models
from springkit.blocks.headings import HeadingBlock
from springkit.blocks.jumplinks import JumplinkMixin
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from cdhweb.pages.blocks.link import InternalPageLinkBlock


class TileExternalLink(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title for this tile.",
        label="Tile Title",
        required=True,
    )

    image = ImageChooserBlock(
        help_text="Image for this tile.",
        label="Tile Image",
        required=False,
    )

    summary = blocks.CharBlock(
        max_length=200,
        help_text="Summary for this tile.",
        label="Tile Summary",
        required=False,
    )

    external_link = blocks.URLBlock(required=True)


class TileInternalPage(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=True)


class StandardTileBlock(JumplinkMixin):
    """
    CMS controlled Standard Tile block
    """

    heading = HeadingBlock(required=False, help_text="Heading for this tile block")

    description = blocks.CharBlock(
        help_text="Description for this tile block",
        label="Description",
        required=False,
    )

    see_more_link = InternalPageLinkBlock(help_text="'See more' link", required=False)

    featured = blocks.BooleanBlock(
        default=False,
        help_text="Check this checkbox to create a visually distinct tile block that stands out from regular tiles on the page.",
        required=False,
    )

    tiles = blocks.StreamBlock(
        [
            ("internal_page_tile", TileInternalPage()),
            ("external_page_tile", TileExternalLink()),
        ],
        min_num=1,
        required=True,
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)

        tiles = value.get("tiles")
        context["tiles"] = tiles
        print(tiles)
        return context

    class Meta:
        template = "cdhpages/blocks/standard_tile_block.html"
        label = "Standard Tile Block"
        icon = "copy"
        group = "Body copy components"
