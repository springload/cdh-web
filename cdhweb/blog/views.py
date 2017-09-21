from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Atom1Feed
from django.views.generic.detail import DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView

from .models import BlogPost


class BlogIndexView(ArchiveIndexView):

    model = BlogPost
    date_field = 'publish_date'
    paginate_by = 7

    def get_queryset(self):
        qs = BlogPost.objects.published() # TODO: published(for_user=self.request.user)
        if self.kwargs.get('year', None):
            qs = qs.filter(publish_date__year=self.kwargs['year'])
        return qs


class BlogYearArchiveView(YearArchiveView):
    date_field = "publish_date"
    make_object_list = True

    def get_queryset(self):
        qs = BlogPost.objects.published() # TODO: published(for_user=self.request.user)
        if self.kwargs.get('year', None):
            qs = qs.filter(publish_date__year=self.kwargs['year'])
        return qs


class BlogDetailView(DetailView):

    model = BlogPost

    def get_queryset(self):
        return BlogPost.objects.published() # TODO: published(for_user=self.request.user)


class RssBlogPostFeed(Feed):
    title = "Center for Digital Humanities @ Princeton University Updates"
    link = "/updates/"
    description = "Updates and news on work from the Center for Digital Humanities @ Princeton University"

    def items(self):
        return BlogPost.objects.order_by('-publish_date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.content


class AtomBlogPostFeed(RssBlogPostFeed):
    feed_type = Atom1Feed
    subtitle = RssBlogPostFeed.description
