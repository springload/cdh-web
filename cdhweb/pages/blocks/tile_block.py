from django.db import models
from springkit.blocks import JumplinkableH2Block
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from cdhweb.pages.blocks.link import InternalPageLinkBlock


class TileExternalLink(blocks.StructBlock):
    title = blocks.CharBlock(
        max_length=100,
        help_text="Title for this tile. If cms page has been chosen for link then you can leave this field blank and the title will default to the short title from the CMS Page.",
        label="Tile Title",
        required=True,
    )

    image = ImageChooserBlock(
        help_text="If cms page has been chosen for link then you can leave this field blank and the image will default to the feed image from the CMS Page.",
        label="Tile Image",
        required=False,
    )

    summary = blocks.CharBlock(
        max_length=200,
        help_text="If cms page has been chosen for link then you can leave this field blank and the summary will default to the summary from the CMS Page.",
        label="Tile Summary",
        required=False,
    )

    external_link = blocks.URLBlock(required=True)


class TileInternalPage(blocks.StructBlock):
    page = blocks.PageChooserBlock(required=True)

    # def get_context(self, value, parent_context=None):
    #     context = super().get_context(value, parent_context=parent_context)
    #     page_instance = value.get('page').specific
    #     context['page'].page_type = type(page_instance).__name__
    #     print(context)
    #     return context


class StandardTileBlock(blocks.StructBlock):
    """
    CMS controlled Standard Tile block
    """

    heading = JumplinkableH2Block(
        required=False, help_text="Heading for this tile block"
    )

    description = blocks.CharBlock(
        help_text="Description for this tile block",
        label="Description",
        required=False,
    )

    see_more_link = InternalPageLinkBlock(help_text="'See more' link", required=False)

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
        print(context)
        return context

    class Meta:
        template = "cdhpages/blocks/standard_tile_block.html"
        label = "Standard Tile Block"
