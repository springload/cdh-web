from datetime import datetime, timedelta

from django.test import TestCase
from django.urls import resolve

from cdhweb.events.models import Event, EventType, Location


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


class TestEvent(TestCase):

    def test_str(self):
        jan15 = datetime(2015, 1, 15)
        event = Event(title='Learning', start_time=jan15, end_time=jan15,
            slug='some-workshop')
        assert str(event) == '%s - %s' % (event.title, jan15.strftime('%b %d, %Y'))


    def test_get_absolute_url(self):
        jan15 = datetime(2015, 1, 15)
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
        jan15 = datetime(2015, 1, 15, hour=16)
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



class TestEventQueryset(TestCase):

    def test_upcoming(self):
        tomorrow = datetime.now() + timedelta(days=1)
        yesterday = datetime.now() - timedelta(days=1)
        event_type = EventType.objects.first()
        next_event = Event.objects.create(start_time=tomorrow, end_time=tomorrow,
            slug='some-workshop', event_type=event_type)
        last_event = Event.objects.create(start_time=yesterday, end_time=yesterday,
            slug='some-workshop', event_type=event_type)

        upcoming = list(Event.objects.upcoming())
        assert next_event in upcoming
        assert last_event not in upcoming

