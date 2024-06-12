from django.utils import timezone
from springkit.blocks.headings import HeadingBlock
from springkit.blocks.jumplinks import JumplinkMixin
from wagtail import blocks

from cdhweb.pages.blocks.link import InternalPageLinkBlock

from .article_index_block import ArticleTileBlock


class EventTileBlock(ArticleTileBlock):
    landing_page = blocks.PageChooserBlock(
        required=True,
        page_type=["events.EventsLandingPage"],
        help_text=(
            "Select the Event Landing Page whose child pages you want to show as "
            "tiles in this block."
        ),
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)

        current_datetime = timezone.now()

        child_pages = (
            value.get("landing_page")
            .get_children()
            .live()
            .public()
            .filter(event__start_time__gt=current_datetime)  # only show upcoming events
            .order_by("event__start_time")  # Sort by date ascending
            .specific()
        )

        max_value = int(value.get("max_articles"))

        tiles = child_pages[:max_value]

        context["tiles"] = tiles
        return context

    class Meta:
        template = "cdhpages/blocks/article_tile_block.html"
        label = "Event Tile Block"
        icon = "calendar-alt"
        group = "Body copy components"
