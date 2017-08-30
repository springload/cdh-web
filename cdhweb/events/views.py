from django.http import HttpResponse
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
import icalendar

from cdhweb.events.models import Event


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


class EventIcalView(EventDetailView):
    model = Event

    def render_to_response(self, context, **response_kwargs):
        cal = icalendar.Calendar()
        cal.add_component(self.object.ical_event())
        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename="%s.ics"' \
            % self.object.slug
        return response


class IcalCalendarView(EventListView):

    def get_queryset(self):
        return super(IcalCalendarView, self).get_queryset().upcoming()

    def render_to_response(self, context, **response_kwargs):
        cal = icalendar.Calendar()
        for event in self.get_queryset():
            cal.add_component(event.ical_event())
        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename="CDH-calendar.ics"'
        return response

