from django.views.generic.detail import DetailView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView


from .models import BlogPost


class BlogIndexView(ArchiveIndexView):

    # same list view can power complete list or filtered version
    # by year, month, whatever
    # - pass year/month/etc filters in context data for display
    #   in the template
    model = BlogPost
    date_field = 'publish_date'

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