from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Event


class EventListView(ListView):

    # same list view can power complete list or filtered version
    # by year, month, whatever
    # - pass year/month/etc filters in context data for display
    #   in the template
    model = Event

    def get_queryset(self):
        # TODO: label based on which events are displayed
        # upcoming? year? (semester?)
        qs = Event.objects.published(for_user=self.request.user)
        if self.kwargs.get('year', None):
            qs = qs.filter(publish_date__year=self.kwargs['year'])
        return qs


class EventDetailView(DetailView):

    model = Event

    def get_queryset(self):
        return Event.objects.published(for_user=self.request.user)

