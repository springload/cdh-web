from springkit.blocks.headings import HeadingBlock
from springkit.blocks.jumplinks import JumplinkMixin
from wagtail import blocks

from cdhweb.pages.blocks.link import InternalPageLinkBlock


class ArticleTileBlock(JumplinkMixin):
    """
    CMS controlled Article Tile block
    """

    heading = HeadingBlock(required=False, help_text="Heading for this tile block")

    description = blocks.CharBlock(
        help_text="Description for this tile block",
        label="Description",
        required=False,
    )

    landing_page = blocks.PageChooserBlock(
        required=True,
        page_type=["blog.BlogLandingPage"],
        help_text=(
            "Select the Blog Landing Page whose child pages you want to show as "
            "tiles in this block."
        ),
    )

    max_articles = blocks.ChoiceBlock(
        choices=[
            (2, "2"),
            (3, "3"),
            (4, "4"),
            (5, "5"),
            (6, "6"),
        ],
        default=3,
        icon="placeholder",
        help_text="Define the maximum number of tiles to show in this group.",
    )

    see_more_link = blocks.CharBlock(
        max_length=80,
        help_text="Set text for the link which takes you to the landing page",
        label="Link title",
        default='See All',
        required=False,
    )
    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        child_pages = (
            value.get("landing_page")
            .get_children()
            .live()
            .public()
            .order_by("-blogpost__first_published_at")  # Sort by date descending
            .specific()
        )

        max_value = int(value.get("max_articles"))

        tiles = child_pages[:max_value]

        context["tiles"] = tiles
        return context

    class Meta:
        template = "cdhpages/blocks/article_tile_block.html"
        label = "Article Tile Block"
        icon = "doc-full"
        group = "Body copy components"
