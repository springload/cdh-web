from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils.feedgenerator import Atom1Feed
from django.views.generic import ListView
from django.views.generic.detail import DetailView

from cdhweb.blog.models import BlogLandingPage, BlogPost
from cdhweb.pages.views import LastModifiedMixin


class BlogLandingPageView(ListView):
    model = BlogLandingPage
    template_name = "blog/blog_landing_page.html"
    context_object_name = "posts"
    paginate_by = 15
    make_object_list = True

    def get_object(self):
        slug = self.kwargs.get("slug")
        return BlogLandingPage.objects.get(slug=slug)

    def get_queryset(self, **kwargs):
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")

        if month and year:
            posts = self.get_object().get_posts_for_year_and_month(
                int(month), int(year)
            )
        elif year:
            posts = self.get_object().get_posts_for_year(int(year))
        else:
            # if month and year are not supplied then supply all posts from newest to oldest
            posts = self.get_object().get_latest_posts()

        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date_list"] = self.get_object().get_list_of_dates()
        context["self"] = self.get_object()
        return context


class RssBlogPostFeed(Feed):
    """Blog post RSS feed"""

    title = "Center for Digital Humanities @ Princeton University Updates"
    link = "/updates/"
    description = "Updates and news on work from the Center for Digital Humanities @ Princeton University"

    def items(self):
        """ten most recent blog posts, ordered by publish date"""
        return BlogPost.objects.live().recent()[:10]

    def item_title(self, item):
        """blog post title"""
        return item.title

    def item_description(self, item):
        """blog post description, for feed content"""
        return item.get_description()

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
