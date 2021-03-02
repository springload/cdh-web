from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.text import Truncator
from django.utils.translation import ugettext_lazy as _
from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, RichText
from mezzanine.utils.models import AdminThumbMixin, upload_to
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         PageChooserPanel, StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, PageManager, PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel

from cdhweb.pages.models import BodyContentBlock, LinkPage
from cdhweb.resources.models import Attachment


class MultiOwnable(models.Model):
    """
    Abstract model based on Mezzanine's :class:`mezzanine.core.models.Ownable`
    to provides ownership of an object for a user, except allows for
    multiple owners.
    """

    users = models.ManyToManyField(User, verbose_name=_("Authors"),
                                   related_name="%(class)ss")

    class Meta:
        abstract = True

    def is_editable(self, request):
        """
        Restrict in-line editing to the objects's owner and superusers.
        """
        return request.user.is_superuser or \
            self.users.filter(id=request.user.id).exists()

    def author_list(self):
        '''comma-separated list of authors'''
        return ', '.join(str(user) for user in self.users.all())
    author_list.short_description = 'Authors'


class BlogPostQuerySet(PageQuerySet):

    def featured(self):
        '''return blog posts that are marked as featured'''
        return self.filter(is_featured=True)

    def recent(self):
        '''sort blog posts by first publication date'''
        return self.order_by('-first_published_at')


class OldBlogPost(Displayable, MultiOwnable, RichText, AdminThumbMixin):
    """
    A blog post with multiple authors. Based on
    :class:`mezzanine.blog.models.BlogPost`.
    """

    # mezzanine blogpost has comments, categoriees, and ratings; do we
    # care about any of those?
    featured_image = FileField(verbose_name=_("Featured Image"),
                               upload_to=upload_to(
                                   "blog.BlogPost.featured_image", "blog"),
                               help_text="Appears on the homepage carousel when post is featured.",
                               format="Image", max_length=255, null=True, blank=True)
    related_posts = models.ManyToManyField("self",
                                           verbose_name=_("Related posts"), blank=True)
    tags = TaggableManager(blank=True)
    attachments = models.ManyToManyField(Attachment, blank=True)
    is_featured = models.BooleanField(verbose_name=_("Featured"), default=False,
                                      help_text="Feature the post in the carousel on the homepage.")

    admin_thumb_field = "featured_image"

    @property
    def short_title(self):
        '''shorter title with ellipsis'''
        return Truncator(self.title).chars(65)

    @property
    def short_description(self):
        '''shorter description with ellipsis'''
        return Truncator(self.description).chars(250)

    # custom manager for additioal queryset filters
    objects = BlogPostQuerySet.as_manager()

    class Meta:
        verbose_name = _("Blog post")
        verbose_name_plural = _("Blog posts")
        ordering = ("-publish_date",)

    def get_absolute_url(self):
        # we don't have to worry about the various url config options
        # that mezzanine has to support; just handle the url style we
        # want to use locally
        return reverse('blog:detail', kwargs={
            'year': self.publish_date.year,
            # force two-digit month
            'month': '%02d' % self.publish_date.month,
            'day': '%02d' % self.publish_date.day,
            'slug': self.slug})


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
BlogPostManager = PageManager.from_queryset(BlogPostQuerySet)


class BlogPostTag(TaggedItemBase):
    """Tags for Blog posts."""
    content_object = ParentalKey(
        "blog.BlogPost", on_delete=models.CASCADE, related_name="tagged_items")


class BlogPost(Page, ClusterableModel):
    """A Blog post, implemented as a Wagtail page."""

    content = StreamField(BodyContentBlock, blank=True)
    featured_image = models.ForeignKey("wagtailimages.image", null=True, blank=True,
                                       on_delete=models.SET_NULL, related_name="+",
                                       help_text="Appears on the homepage carousel when post is featured.")
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, editable=False)
    is_featured = models.BooleanField(
        default=False, help_text="Show the post in the carousel on the homepage.")
    # TODO attachments (#245)

    # can only be created underneath special link page
    parent_page_types = ["blog.BlogLinkPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldRowPanel((ImageChooserPanel("featured_image"),
                       FieldPanel("is_featured"))),
        StreamFieldPanel("content"),
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("tags")
    ]

    # custom manager/queryset logic
    objects = BlogPostManager()

    context_object_name = "post"

    class Meta:
        ordering = ("-first_published_at",)

    @property
    def short_title(self):
        """Shorter title with ellipsis."""
        return Truncator(self.title).chars(65)

    @property
    def short_description(self):
        """Shorter description with ellipsis."""
        return Truncator(self.seo_description).chars(250)

    def get_url_parts(self, *args, **kwargs):
        """Custom blog post URLs of the form /updates/2014/03/01/my-post."""
        url_parts = super().get_url_parts(*args, **kwargs)
        # NOTE evidently this can sometimes be None; unclear why – perhaps it
        # gets called in a context where the request is unavailable? Only
        # happens in QA, not locally.
        if url_parts:
            site_id, root_url, _ = url_parts
            page_path = reverse("blog:detail", kwargs={
                "year": self.first_published_at.year,
                # force two-digit month and day
                "month": "%02d" % self.first_published_at.month,
                "day": "%02d" % self.first_published_at.day,
                "slug": self.slug,
            })
            return site_id, root_url, page_path


class BlogLinkPage(LinkPage):
    """Container page that defines where blog posts can be created."""
    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a BlogPost; this is so that
    # Events made in the admin automatically are created here.
    subpage_types = [BlogPost]
