from datetime import datetime

from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.views.generic.dates import (
    ArchiveIndexView,
    MonthArchiveView,
    YearArchiveView,
)
from django.core.paginator import Paginator

from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView
from django.views.generic import ListView

from cdhweb.blog.models import BlogPost, BlogLandingPage
from cdhweb.pages.views import LastModifiedListMixin, LastModifiedMixin


class BlogPostMixinView(object):
    """Mixin that sets model to BlogPost and orders/filters queryset."""

    model = BlogPost
    lastmodified_attr = "last_published_at"

    def get_queryset(self):
        """Return published posts with most recent first."""
        return BlogPost.objects.live().recent()


class BlogPostArchiveMixin(BlogPostMixinView, LastModifiedListMixin):
    """Mixin with common settings for blogpost archive views"""

    date_field = "first_published_at"
    context_object_name = "posts"
    make_object_list = True
    paginate_by = 12
    template_name = "blog/blogpost_archive.html"


class BlogIndexView(BlogPostArchiveMixin, ArchiveIndexView):
    """Main blog post list view"""

    date_list_period = "month"

    def get_queryset(self):
        return super().get_queryset().prefetch_related("page_ptr")

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({"page_title": "Latest Updates"})
        return context
    
class BlogLandingPageView(TemplateView):
    model = BlogLandingPage
    template_name = "blog/blog_landing_page.html"
    context_object_name = "posts"
    paginate_by = 3
    make_object_list = True

    def get_object(self):
        slug = self.kwargs.get('slug')
        return BlogLandingPage.objects.get(slug=slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        month = self.kwargs.get("month")
        year = self.kwargs.get("year")

        if month and year:
            posts = self.get_object().get_posts_for_year_and_month(
                int(month), int(year)
            )
        elif year:
            posts = self.get_object().get_posts_for_year(
                int(year)
            )
        else:
            # if month and year are not supplied then supply all posts from newest to oldest
            posts = self.get_object().get_latest_posts()

        context["posts"] = posts


        paginator = Paginator(posts, per_page=3)
        page_obj = paginator.get_page(request.GET.get("page"))
        context["page_obj"] = page_obj

        context["date_list"] = self.get_object().get_list_of_dates()
        context["self"] = self.get_object()

        return context


class BlogYearArchiveView(BlogPostArchiveMixin, YearArchiveView):
    """Blog post archive by year"""

    def get_context_data(self, *args, **kwargs):
        context = super(BlogYearArchiveView, self).get_context_data(*args, **kwargs)
        context.update(
            {
                "date_list": BlogPost.objects.dates(
                    self.date_field, "month", order="DESC"
                ),
                "page_title": "%s Updates" % self.kwargs["year"],
            }
        )
        return context


class BlogMonthArchiveView(BlogPostArchiveMixin, MonthArchiveView):
    """Blog post archive by month"""

    month_format = "%m"

    def get_context_data(self, *args, **kwargs):
        context = super(BlogMonthArchiveView, self).get_context_data(*args, **kwargs)
        # current requested month/year for display
        date = datetime.strptime("%(year)s %(month)s" % self.kwargs, "%Y %m")
        context.update(
            {
                "date_list": BlogPost.objects.dates(
                    self.date_field, "month", order="DESC"
                ),
                "page_title": "%s Updates" % date.strftime("%B %Y"),
            }
        )
        return context


class BlogDetailView(BlogPostMixinView, DetailView, LastModifiedMixin):
    """Blog post detail view"""

    context_object_name = "page"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        return self.object.serve(request, *args, **kwargs)


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
