import pytest
from django.core.exceptions import ValidationError
from datetime import timezone as tz
from datetime import timedelta
from django.utils import timezone

from cdhweb.events.models import Event, EventType, Location, EventsLinkPage
from cdhweb.pages.tests.conftest import to_streamfield_safe

class TestSpeaker:
    def test_str(self, lecture):
        """speaker should be identified by person and event"""
        speaker = lecture.speakers.first()
        assert str(
            speaker
        ) == "john lecturer at testing lecture - %s" % lecture.start_time.strftime(
            "%b %d, %Y"
        )


class TestEventType:
    def test_str(self):
        """event type string should be type name"""
        evtype = EventType(name="Workshop")
        assert str(evtype) == evtype.name


class TestLocation:
    def test_str(self):
        """location string should be location short name or name"""
        loc = Location(name="Center for Finger Studies")
        assert str(loc) == loc.name
        loc.short_name = "CFS"
        assert str(loc) == loc.short_name

    def test_displayname(self):
        """location display name should include address if diff from name"""
        loc = Location(name="Center for Finger Studies")
        assert str(loc.display_name) == loc.name
        loc.address = "Waterstone Library, Floor 3"
        assert str(loc.display_name) == "%s, %s" % (loc.name, loc.address)

        # name and address thesame
        loc = Location(name="101 East Pyne", address="101 East Pyne")
        assert str(loc.display_name) == loc.name

    def test_clean(self):
        """non-virtual location without address should be invalid"""
        # location with no address raises ValidationError
        loc = Location(name="Center for Finger Studies")
        with pytest.raises(ValidationError):
            loc.clean()

        # virtual location with no address is fine
        loc.is_virtual = True
        loc.clean()


class TestEventQueryset:
    def make_second_course(self):
        """Create a course that will happen in 2080. An extra course is needed
        to test sorting"""
        course_type = EventType.objects.get_or_create(name="Course")[0]
        start_time = timezone.datetime(2080, 2, 2).astimezone(tz.utc)
        end_time = timezone.datetime(2080, 4, 27).astimezone(tz.utc)
        course = Event(
            title="second testing course",
            body=to_streamfield_safe("<p>February 2080 History of Digital Humanities</p>"),
            start_time=start_time,
            end_time=end_time,
            type=course_type,
        )
        course.last_published_at = start_time - timedelta(days=10)
        link_page = EventsLinkPage.objects.get(slug="events")
        link_page.add_child(instance=course)
        link_page.save()
        return course

    def test_upcoming(self, events):
        """upcoming should include all events that haven't started yet"""
        self.make_second_course()
        upcoming = list(Event.objects.upcoming())
        assert events["deadline"] in upcoming
        assert events["workshop"] not in upcoming
        assert events["lecture"] not in upcoming

        # Ensure that the order is correct
        assert upcoming[0].start_time < upcoming[1].start_time


    def test_recent(self, events):
        """recent should include past events with most recent first"""
        recent = list(Event.objects.recent())
        assert events["deadline"] not in recent
        assert recent[0] == events["workshop"]
        assert recent[1] == events["lecture"]
