from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.search import index

from .utils import LengthOverrideWidget


class HomePageHeroMixin(models.Model):
    summary = models.TextField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name="Page Summary",
        help_text="Text that supports / qualifies the hero header and gives people a sense of who you are",
    )

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that conveys sense of site / brand",
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text=""" Heading on the larger hero banner at top of the page.
                                Ideal length < 45 characters (around 5 words)""",
                    widget=LengthOverrideWidget(max_length=80),
                ),
                FieldPanel("summary"),
                FieldPanel("hero_image"),
            ],
            "HomePage Hero",
        )
    ]

    class Meta:
        abstract = True


class StandardHeroMixin(models.Model):
    summary = models.TextField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Page Summary",
        help_text="""Short introduction to the page, aim for max two clear sentences (max. 200 chars). 
        Used to orient the user and help them identify relevancy of the page to meet their needs. """,
    )

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Optional image to support intent of the page.",
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel(
                    "title",
                    help_text="""Main heading for the page. Ideally up to five words long (max.100 chars).""",
                    widget=LengthOverrideWidget(max_length=100),
                ),
                FieldPanel("summary"),
                FieldPanel("hero_image"),
            ],
            "Standard Hero",
        )
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("summary"),
    ]

    class Meta:
        abstract = True
