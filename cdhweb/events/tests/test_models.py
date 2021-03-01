import pytest
from django.core.exceptions import ValidationError

from cdhweb.events.models import EventType, Location, Event


class TestEventType:

    def test_str(self):
        """event type string should be type name"""
        evtype = EventType(name='Workshop')
        assert str(evtype) == evtype.name


class TestLocation:

    def test_str(self):
        """location string should be location short name or name"""
        loc = Location(name='Center for Finger Studies')
        assert str(loc) == loc.name
        loc.short_name = 'CFS'
        assert str(loc) == loc.short_name

    def test_displayname(self):
        """location display name should include address if diff from name"""
        loc = Location(name='Center for Finger Studies')
        assert str(loc.display_name) == loc.name
        loc.address = 'Waterstone Library, Floor 3'
        assert str(loc.display_name) == '%s, %s' % (loc.name, loc.address)

        # name and address thesame
        loc = Location(name='101 East Pyne', address='101 East Pyne')
        assert str(loc.display_name) == loc.name

    def test_clean(self):
        """non-virtual location without address should be invalid"""
        # location with no address raises ValidationError
        loc = Location(name='Center for Finger Studies')
        with pytest.raises(ValidationError):
            loc.clean()

        # virtual location with no address is fine
        loc.is_virtual = True
        loc.clean()


class TestEventQueryset:

    def test_upcoming(self, events):
        """upcoming should include all events that haven't started yet"""
        upcoming = list(Event.objects.upcoming())
        assert events["deadline"] in upcoming
        assert events["workshop"] not in upcoming
        assert events["lecture"] not in upcoming

    def test_recent(self, events):
        """recent should include past events with most recent first"""
        recent = list(Event.objects.recent())
        assert events["deadline"] not in recent
        assert recent[0] == events["workshop"]
        assert recent[1] == events["lecture"]
