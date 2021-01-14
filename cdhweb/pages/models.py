from random import shuffle

import bleach
from django.apps import apps
from django.conf import settings
from django.db import models
from django.template.defaultfilters import striptags, truncatechars_html
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core.blocks import (RichTextBlock, StreamBlock, StructBlock,
                                 TextBlock)
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core.models import Page
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from wagtail.snippets.models import register_snippet
from wagtailmenus.models import AbstractLinkPage


#: common features for paragraph text
PARAGRAPH_FEATURES = [
    'h3', 'h4', 'bold', 'italic', 'link', 'ol', 'ul',
    'hr', 'blockquote', 'document', 'superscript', 'subscript',
    'strikethrough', 'code'
]

#: help text for image alternative text
ALT_TEXT_HELP = """Alternative text for visually impaired users to
briefly communicate the intended message of the image in this context."""


class CaptionedImageBlock(StructBlock):
    """:class:`~wagtail.core.blocks.StructBlock` for an image with
    alternative text and optional formatted caption, so
    that both caption and alternative text can be context-specific."""
    image = ImageChooserBlock()
    alternative_text = TextBlock(required=True, help_text=ALT_TEXT_HELP)
    caption = RichTextBlock(
        features=["bold", "italic", "link", "superscript"],
        required=False)

    class Meta:
        icon = "image"
        template = "cdhpages/snippets/captioned_image.html"


class SVGImageBlock(StructBlock):
    """:class:`~wagtail.core.blocks.StructBlock` for an SVG image with
    alternative text and optional formatted caption. Separate from
    :class:`CaptionedImageBlock` because Wagtail image handling
    does not work with SVG."""
    extended_description_help = """This text will only be read to \
    non-sighted users and should describe the major insights or \
    takeaways from the graphic. Multiple paragraphs are allowed."""

    image = DocumentChooserBlock()
    alternative_text = TextBlock(required=True, help_text=ALT_TEXT_HELP)
    caption = RichTextBlock(
        features=["bold", "italic", "link", "superscript"],
        required=False)
    extended_description = RichTextBlock(
        features=["p"], required=False, help_text=extended_description_help)

    class Meta:
        icon = "image"
        label = "SVG"
        template = "cdhpages/snippets/svg_image.html"


class BodyContentBlock(StreamBlock):
    '''Common set of blocks available in StreamFields for body text.'''
    # allow h2 in regular paragraphs; insert before h3 for logical display
    paragraph = RichTextBlock(features=["h2"] + PARAGRAPH_FEATURES)
    image = CaptionedImageBlock()
    svg_image = SVGImageBlock()
    document = DocumentChooserBlock()
    embed = EmbedBlock()
    #: used to hold content migrated from mezzanine via a "kitchen-sink"
    #: approach; virtually all html tags are allowed. should NOT be used when
    #: creating new pages.
    migrated = RichTextBlock(
        features=settings.RICHTEXT_ALLOWED_TAGS, icon="warning")


class PagePreviewDescriptionMixin(models.Model):
    '''Page mixin with logic for page preview content. Adds an optional
    richtext description field, and methods to get description and plain-text
    description, for use in previews on the site and plain-text metadata
    previews.'''

    # adapted from PPA; does not allow <p> tags in description
    #: brief description for preview display
    description = RichTextField(
        blank=True, features=['bold', 'italic'],
        help_text='Optional. Brief description for preview display. Will ' +
        'also be used for search description (without tags), if one is ' +
        'not entered.')
    #: maximum length for description to be displayed
    max_length = 225
    # (tags are omitted by subsetting default ALLOWED_TAGS)
    #: allowed tags for bleach html stripping in description
    allowed_tags = list((set(bleach.sanitizer.ALLOWED_TAGS) -
                         set(['a', 'blockquote'])))  # additional tags to remove

    class Meta:
        abstract = True

    def get_description(self):
        '''Get formatted description for preview. Uses description field
        if there is content, otherwise uses beginning of the body content.'''

        description = ''

        # use description field if set
        # use striptags to check for empty paragraph
        if striptags(self.description):
            description = self.description

        # if not, use beginning of body content
        else:
            # Iterate over blocks and use content from first paragraph content
            for block in self.body:
                if block.block_type == 'paragraph':
                    description = block
                    # stop after the first instead of using last
                    break

        description = bleach.clean(
            str(description),
            tags=self.allowed_tags,
            strip=True
        )
        # truncate either way
        return truncatechars_html(description, self.max_length)

    def get_plaintext_description(self):
        '''Get plain-text description for use in metadata. Uses
        search_description field if set; otherwise uses the result of
        :meth:`get_description` with tags stripped.'''

        if self.search_description.strip():
            return self.search_description
        return striptags(self.get_description())


class LinkPage(AbstractLinkPage):
    pass


class ContentPage(Page, PagePreviewDescriptionMixin):
    '''Basic content page model.'''

    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    # TODO attachments

    content_panels = Page.content_panels + [
        FieldPanel('description'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['HomePage', 'LandingPage', 'ContentPage']
    subpage_types = ['ContentPage']


class LandingPage(Page):
    '''Page type that aggregates and displays multiple :class:`ContentPage`s.'''

    #: short sentence overlaid on the header image
    tagline = models.CharField(max_length=255)
    #: image that will be used for the header
    header_image = models.ForeignKey('wagtailimages.image', null=True,
                                     blank=True, on_delete=models.SET_NULL, related_name='+')  # no reverse relationship
    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [
        FieldPanel('tagline'),
        ImageChooserPanel('header_image'),
        StreamFieldPanel('body'),
    ]

    parent_page_types = ['HomePage']
    subpage_types = ['ContentPage']


class HomePage(Page):
    '''A home page that aggregates and displays featured content.'''

    #: main page text
    body = StreamField(BodyContentBlock, blank=True)

    search_fields = Page.search_fields + [index.SearchField('body')]
    content_panels = Page.content_panels + [StreamFieldPanel('body')]

    parent_page_types = [Page]  # only root
    subpage_types = ['LandingPage', 'ContentPage']

    class Meta:
        verbose_name = 'Homepage'

    def get_context(self, request):
        '''Add featured updates, projects, and events to the page context.'''
        context = super().get_context(request)

        # FIXME an ImportError is thrown when classes in this module are
        # imported elsewhere if any of these three models are imported at the
        # top. Why?
        BlogPost = apps.get_model("blog", "blogpost")
        Project = apps.get_model("projects", "project")
        Event = apps.get_model("events", "event")

        # add up to 6 featured updates, otherwise use 3 most recent updates
        updates = BlogPost.objects.featured().published().recent()[:6]
        if not updates.exists():
            updates = BlogPost.objects.published().recent()[:3]
        context['updates'] = updates

        # add up to 4 highlighted, published projects
        projects = list(Project.objects.published().highlighted())
        shuffle(projects)
        context['projects'] = projects[:4]

        # add up to 3 upcoming, published events
        context['events'] = Event.objects.published().upcoming()[:3]

        return context


@register_snippet
class PageIntro(models.Model):
    '''Snippet for optional page intro text on for pages generated from
    django views not managed by wagtail'''
    page = models.OneToOneField(LinkPage, on_delete=models.CASCADE)
    #: intro text
    paragraph = RichTextField(features=PARAGRAPH_FEATURES)

    panels = [
        FieldPanel('page'),
        FieldPanel('paragraph'),
    ]

    def __str__(self):
        return self.page.title
