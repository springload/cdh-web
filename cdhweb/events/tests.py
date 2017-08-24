from django.test import TestCase

from datetime import datetime, timedelta
from .models import Event, EventType, Location


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
        assert evt.get_absolute_url() == '/events/2015/01/some-workshop/'


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
        print(upcoming)
        assert next_event in upcoming
        assert last_event not in upcoming

