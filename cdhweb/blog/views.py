from typing import Any
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.views.generic.detail import DetailView
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404

from cdhweb.blog.models import BlogPost


class RssBlogPostFeed(Feed):
    """Blog post RSS feed"""

    title = "Center for Digital Humanities @ Princeton University Updates"
    link = "/blog/"  # Not technically correct, but currently best-match
    description = "Updates and news on work from the Center for Digital Humanities @ Princeton University"

    def items(self):
        """ten most recent blog posts, ordered by publish date"""
        return BlogPost.objects.live().recent()[:10]

    def item_title(self, item):
        """blog post title"""
        return item.title

    def item_description(self, item):
        """blog post description, for feed content"""
        return item.feeds_description

    def item_link(self, item):
        """absolute link to blog post"""
        return item.get_full_url()

    def item_author_name(self, item):
        """author of the blog post; comma-separated list for multiple"""
        return item.author_list

    def item_author_email(self, item):
        """author email, if there is only one author"""
        if item.authors.count() == 1:
            return item.authors.first().person.email

    def item_author_link(self, item):
        """link to author profile page, if there is only one author and
        the author has a published profile"""
        if item.authors.count() == 1:
            return item.authors.first().person.profile_url

    def item_pubdate(self, item):
        """publication date"""
        return item.first_published_at

    def item_updateddate(self, item):
        """last modified date"""
        return item.last_published_at

    def item_categories(self, item):
        """keyword category terms"""
        return [str(tag) for tag in item.tags.all()]


class AtomBlogPostFeed(RssBlogPostFeed):
    """Blog post Atom feed"""

    feed_type = Atom1Feed
    subtitle = RssBlogPostFeed.description

class BlogPostRedirectView(RedirectView):
    pattern_name = "blog-detail"
    
    def get_redirect_url(self, *args, **kwargs):
        post = get_object_or_404(BlogPost, slug=kwargs["slug"])
        return post.url