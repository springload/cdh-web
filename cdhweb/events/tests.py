from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import resolve
from django.utils import timezone
import icalendar
import pytz

from cdhweb.events.models import Event, EventType, Location
from cdhweb.resources.utils import absolutize_url


class TestEventType(TestCase):

    def test_str(self):
        evtype = EventType(name='Workshop')
        assert str(evtype) == evtype.name


class TestLocation(TestCase):

    def test_str(self):
        loc = Location(name='Center for Finger Studies')
        assert str(loc) == loc.name
        loc.short_name = 'CFS'
        assert str(loc) == loc.short_name

    def test_displayname(self):
        loc = Location(name='Center for Finger Studies')
        assert str(loc.display_name) == loc.name
        loc.address = 'Waterstone Library, Floor 3'
        assert str(loc.display_name) == '%s, %s' % (loc.name, loc.address)


class TestEvent(TestCase):

    def test_str(self):
        jan15 = datetime(2015, 1, 15, tzinfo=timezone.get_default_timezone())
        event = Event(title='Learning', start_time=jan15, end_time=jan15,
            slug='some-workshop')
        assert str(event) == '%s - %s' % (event.title, jan15.strftime('%b %d, %Y'))


    def test_get_absolute_url(self):
        jan15 = datetime(2015, 1, 15, tzinfo=timezone.get_default_timezone())
        evt = Event(start_time=jan15, end_time=jan15,
            slug='some-workshop')
        # single-digit months should be converted to two-digit for url
        resolved_url = resolve(evt.get_absolute_url())
        assert resolved_url.namespace == 'event'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['year'] == str(evt.start_time.year)
        assert resolved_url.kwargs['month'] == '%02d' % evt.start_time.month
        assert resolved_url.kwargs['slug'] == evt.slug


    def test_when(self):
        # same day, both pm
        jan15 = datetime(2015, 1, 15, hour=16, tzinfo=timezone.get_default_timezone())
        end = jan15 + timedelta(hours=1, minutes=30)
        event = Event(start_time=jan15, end_time=end)
        # start day month date time (no pm), end time (pm)
        assert event.when() == '%s - %s' % (jan15.strftime('%B %d %I:%M'),
                                            end.strftime('%I:%M %p'))

        # same day, starting in am and ending in pm
        event.start_time = jan15 - timedelta(hours=10)
        # should include am on start time
        assert event.when() == '%s - %s' % \
            (event.start_time.strftime('%B %d %I:%M %p'),
             end.strftime('%I:%M %p'))

        # different days, same month
        event.start_time = jan15 + timedelta(days=1)
        assert event.when() == '%s - %s' % \
            (event.start_time.strftime('%B %d %I:%M'),
             end.strftime('%d %I:%M %p'))

        # different timezone should get localized to current timezone
        event.start_time = datetime(2015, 1, 15, hour=20, tzinfo=pytz.UTC)
        event.end_time = event.start_time + timedelta(hours=12)
        assert '3:00 PM' in event.when()

    def test_ical_event(self):
        jan15 = datetime(2015, 1, 15, hour=16)
        end = jan15 + timedelta(hours=1, minutes=30)
        loc = Location(name='Center for Finger Studies')
        description = 'A revelatory experience'
        event = Event(start_time=jan15, end_time=end,
            title='DataViz Workshop', location=loc,
            content='<p>%s</p>' % description, slug='dataviz-workshop')
        ical = event.ical_event()
        assert isinstance(ical, icalendar.Event)
        assert ical['uid'] == absolutize_url(event.get_absolute_url())
        assert ical['summary'] == event.title
        # Dates are in this format, as bytes: 20150115T160000
        assert ical['dtstart'].to_ical() == \
            event.start_time.strftime('%Y%m%dT%H%M%S').encode()
        assert ical['dtend'].to_ical() == \
            event.end_time.strftime('%Y%m%dT%H%M%S').encode()
        assert ical['location'] == loc.display_name
        # description should have tags stripped
        assert ical['description'].to_ical() == description.encode()


class TestEventQueryset(TestCase):

    def test_upcoming(self):
        # use django timezone util for timezone-aware datetime
        tomorrow = timezone.now() + timedelta(days=1)
        yesterday = timezone.now() - timedelta(days=1)
        event_type = EventType.objects.first()
        next_event = Event.objects.create(start_time=tomorrow, end_time=tomorrow,
            slug='some-workshop', event_type=event_type)
        last_event = Event.objects.create(start_time=yesterday, end_time=yesterday,
            slug='some-workshop', event_type=event_type)

        upcoming = list(Event.objects.upcoming())
        assert next_event in upcoming
        assert last_event not in upcoming

        today = timezone.now()
        earlier_today = datetime(today.year, today.month, today.day,
            tzinfo=timezone.get_default_timezone())
        earlier_event = Event.objects.create(start_time=earlier_today,
            end_time=earlier_today + timedelta(hours=1),
            slug='another-workshop', event_type=event_type)

        assert earlier_event in list(Event.objects.upcoming())


class TestViews(TestCase):

    def test_event_ical(self):
        jan15 = datetime(2015, 1, 15, hour=16,
            tzinfo=timezone.get_default_timezone()) # make timezone aware
        end = jan15 + timedelta(hours=1, minutes=30)
        loc = Location.objects.create(name='Center for Finger Studies')
        description = 'A revelatory experience'
        event_type = EventType.objects.first()
        event = Event.objects.create(start_time=jan15, end_time=end,
            title='DataViz Workshop', location=loc, event_type=event_type,
            content='<p>%s</p>' % description, slug='dataviz-workshop')
        response = self.client.get(event.get_ical_url())

        assert response['content-type'] == 'text/calendar'
        assert response['Content-Disposition'] == \
            'attachment; filename="%s.ics"' % event.slug

        # parsable as ical calendar
        cal = icalendar.Calendar.from_ical(response.content)
        # includes the requested event
        assert cal.subcomponents[0]['uid'] == absolutize_url(event.get_absolute_url())


