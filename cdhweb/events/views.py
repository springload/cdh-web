from django.http import HttpResponse
from django.views.generic.base import RedirectView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView
from django.views.generic.detail import DetailView
from django.shortcuts import get_object_or_404
import icalendar

from cdhweb.events.models import Event


class EventMixinView(object):
    '''View mixin that sets model to Event and returns a
    published Event queryset.'''
    model = Event

    def get_queryset(self):
        # use displayable manager to find published events only
        # (or draft profiles for logged in users with permission to view)
        return Event.objects.published() # TODO: published(for_user=self.request.user)


class UpcomingEventsView(EventMixinView, ArchiveIndexView):
    date_field = "start_time"
    allow_future = True
    context_object_name = 'events'

    # NOTE: can't use get_queryset to restrict to upcoming because
    # that affects the archive date list as well; restricting to upcoming
    # events in get_context_data instaed
    def get_context_data(self, *args, **kwargs):
        context = super(UpcomingEventsView, self).get_context_data(*args, **kwargs)
        context['events'] = context['events'].upcoming()
        return context


class EventYearArchiveView(EventMixinView, YearArchiveView):
    date_field = "start_time"
    make_object_list = True
    allow_future = True


class EventDetailView(EventMixinView, DetailView):
    pass


class EventRedirectView(RedirectView):
    '''Redirect from CDH website v1.0 pk-based urls to new date + slug urls'''
    permanent = True
    query_string = False

    def get_redirect_url(self, *args, **kwargs):
        event = get_object_or_404(Event, pk=kwargs['pk'])
        return event.get_absolute_url()


class EventIcalView(EventDetailView):

    def render_to_response(self, context, **response_kwargs):
        cal = icalendar.Calendar()
        cal.add_component(self.object.ical_event())
        response = HttpResponse(cal.to_ical(), content_type="text/calendar")
        response['Content-Disposition'] = 'attachment; filename="%s.ics"' \
            % self.object.slug
        return response


# ical calendar for all upcoming events
# TODO when we can get to it
# class IcalCalendarView(EventListView):

#     def get_queryset(self):
#         return super(IcalCalendarView, self).get_queryset().upcoming()

#     def render_to_response(self, context, **response_kwargs):
#         cal = icalendar.Calendar()
#         # TODO: required to be compliant
#         # cal.add('prodid', '-//My calendar product//mxm.dk//')
#         # cal.add('version', '2.0')
#         for event in self.get_queryset():
#             cal.add_component(event.ical_event())
#         # TODO: should support cancelled events if possible
#         response = HttpResponse(cal.to_ical(), content_type="text/calendar")
#         response['Content-Disposition'] = 'attachment; filename="CDH-calendar.ics"'
#         return response

