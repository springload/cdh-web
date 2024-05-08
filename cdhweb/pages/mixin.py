from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel


class HomePageHeroMixin(models.Model):
    title = models.CharField(
        max_length=45,
        blank=True,
        null=False,
        verbose_name="Hero title",
        help_text="Heading on the larger hero banner at top of the page",
    )

    summary = models.TextField(
        max_length=150,
        blank=True,
        null=False,
        verbose_name="Page Summary",
        help_text="Text that supports / qualifies the hero header and gives people a sense of who you are",
    )

    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image that conveys sense of site / brand",
    )

    content_panels = [
        MultiFieldPanel(
            [
                TitleFieldPanel("title"),
                FieldPanel("summary"),
                FieldPanel("hero_image"),
            ],
            "HomePage Hero",
        )
    ]

    class Meta:
        abstract = True
