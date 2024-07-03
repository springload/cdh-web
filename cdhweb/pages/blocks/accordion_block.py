from collections.abc import Iterable

from django.db import models
from springkit.blocks.headings import HeadingBlock
from springkit.blocks.jumplinks import JumplinkMixin
from wagtail import blocks


class AccordionBlock(JumplinkMixin):
    """
    A list of accordion items

    """

    class Meta:
        template = "cdhpages/blocks/accordion_block.html"
        label = "Accordion"
        icon = "cogs"
        group = "Body copy components"

    heading = HeadingBlock(required=False)

    description = blocks.RichTextBlock(
        features=["bold", "italic", "link", "document-link"], required=False
    )

    accordion_items = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "heading",
                    blocks.CharBlock(
                        verbose_name="Accordion Title", required=True, max_length=80
                    ),
                ),
                (
                    "body",
                    blocks.RichTextBlock(
                        features=[
                            "bold",
                            "italic",
                            "link",
                            "ol",
                            "ul",
                            "document-link",
                            "h3",
                            "h4",
                        ],
                        help_text="Only use H3 if you have not set an overall heading for the accordion block.",
                    ),
                ),
            ]
        )
    )


class ProjectAccordion(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/accordion_block.html"
        label = "Project Accordion"
        icon = "cogs"

    class AccordionTitles(models.TextChoices):
        CODE = "code", "Code"
        DATA = "data", "Data"
        DOCUMENTATION = "documentation", "Documentation"
        RELATED_COURSES = (
            "related_courses_and_course_modules",
            "Related Courses and Course Modules",
        )
        PROJECT_PEER_REVIEW = "project_peer_review", "Project Peer Review"

    accordion_items = blocks.ListBlock(
        blocks.StructBlock(
            [
                (
                    "heading",
                    blocks.ChoiceBlock(
                        choices=AccordionTitles.choices,
                        required=True,
                    ),
                ),
                (
                    "body",
                    blocks.RichTextBlock(
                        features=[
                            "bold",
                            "italic",
                            "link",
                            "ol",
                            "ul",
                            "document-link",
                            "h3",
                            "h4",
                        ],
                    ),
                ),
            ]
        )
    )
