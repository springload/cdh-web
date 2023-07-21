from datetime import datetime, timedelta

import icalendar
import pytest
import pytz
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import strip_tags
from wagtail.test.utils import WagtailPageTests

from cdhweb.events.models import Event, EventsLinkPage, Speaker
from cdhweb.pages.models import ContentPage, LinkPage
from cdhweb.people.models import Person


class TestEvent:
    def test_str(self, workshop):
        """event string should be its title and start date/time"""
        # make start time into a known datetime for testing
        jan15 = datetime(2015, 1, 15, tzinfo=timezone.get_default_timezone())
        workshop.start_time = jan15
        assert str(workshop) == "testing workshop - Jan 15, 2015"

    def test_get_url(self, workshop):
        """event URL should include two-digit month, year, and slug"""
        # make start time into a known datetime for testing; january -> 01
        jan15 = datetime(2015, 1, 15, tzinfo=timezone.get_default_timezone())
        workshop.start_time = jan15
        workshop.end_time = jan15
        assert workshop.get_url().strip("/").split("/") == [
            "events",
            "2015",
            "01",
            "testing-workshop",
        ]

    def test_when(self, workshop):
        """event should report time lowercased, without repeating am/pm"""
        # same day, both pm
        jan15 = datetime(2015, 1, 15, hour=16, tzinfo=timezone.get_default_timezone())
        end = jan15 + timedelta(hours=1, minutes=30)
        workshop.start_time = jan15
        workshop.end_time = end
        # start day month date time (no pm), end time (pm)
        assert workshop.when() == "%s – %s" % (
            jan15.strftime("%b %d %-I:%M"),
            end.strftime("%-I:%M %p").lower(),
        )

        # same day, starting in am and ending in pm
        workshop.start_time = jan15 - timedelta(hours=10)
        # should include am on start time
        # NOTE: %-I should be equivalent to %I with lstrip("0")
        assert workshop.when() == "%s %s – %s" % (
            workshop.start_time.strftime("%b %d %-I:%M"),
            workshop.start_time.strftime("%p").lower(),
            end.strftime("%I:%M %p").lstrip("0").lower(),
        )

        # different days, same month
        workshop.start_time = jan15 + timedelta(days=1)
        assert workshop.when() == "%s – %s %s" % (
            workshop.start_time.strftime("%b %d %-I:%M"),
            end.strftime("%d %-I:%M"),
            end.strftime("%p").lower(),
        )

        # different timezone should get localized to current timezone
        workshop.start_time = datetime(2015, 1, 15, hour=20, tzinfo=pytz.UTC)
        workshop.end_time = workshop.start_time + timedelta(hours=12)
        assert "3:00 pm" in workshop.when()

        # different months
        end = jan15 + timedelta(days=35)
        workshop.start_time = jan15
        workshop.end_time = end
        # month name should display
        assert end.strftime("%b") in workshop.when()

        # different months, same day
        feb15 = datetime(2015, 2, 15, hour=16, tzinfo=timezone.get_default_timezone())
        workshop.start_time = jan15
        workshop.end_time = feb15
        assert workshop.start_time.strftime("%b %d") in workshop.when()
        assert workshop.end_time.strftime("%b %d") in workshop.when()

    def test_duration(self, events):
        """event should report duration as a timedelta"""
        # workshop duration is 2hrs
        assert events["workshop"].duration() == timedelta(hours=2)
        # lecture duration is 1hr
        assert events["lecture"].duration() == timedelta(hours=1)
        # should work with days also
        events["workshop"].end_time = events["workshop"].start_time + timedelta(days=1)
        assert events["workshop"].duration().days == 1

    def test_ical_event(self, workshop, zoom_location):
        """event should export itself as ical (.ics) file"""
        ical = workshop.ical_event()
        fullurl = workshop.get_full_url()
        assert isinstance(ical, icalendar.Event)
        assert ical["uid"] == fullurl
        assert ical["summary"] == workshop.title
        # Dates are in this format, as bytes: 20150115T160000
        assert (
            ical["dtstart"].to_ical()
            == workshop.start_time.strftime("%Y%m%dT%H%M%SZ").encode()
        )
        assert (
            ical["dtend"].to_ical()
            == workshop.end_time.strftime("%Y%m%dT%H%M%SZ").encode()
        )
        assert ical["location"] == workshop.location.display_name
        # description should have tags stripped
        assert strip_tags(workshop.body) in ical["description"].to_ical().decode()
        assert fullurl in ical["description"].to_ical().decode()
        # change event to a virtual location & add join url
        workshop.location = zoom_location
        workshop.join_url = "princeton.zoom.us/my/zoomroom"
        # ical event should have join URL set as location
        ical = workshop.ical_event()
        assert ical["location"] == "princeton.zoom.us/my/zoomroom"

    def test_is_virtual(self, workshop, lecture):
        """events in virtual locations should show as virtual"""
        # event in non-virtual location (CDH) isn't virtual
        assert not workshop.is_virtual()
        # event in virtual location (zoom) is virtual
        assert lecture.is_virtual()

    def test_type_required(self, events_link_page, cdh_location):
        """events should require an event type on creation"""
        # create without a type; should fail
        reading_grp = Event(
            title="testing reading group",
            body="my description",
            start_time=timezone.now(),
            end_time=timezone.now(),
            location=cdh_location,
        )
        with pytest.raises(ValidationError):
            events_link_page.add_child(instance=reading_grp)

    def test_speaker_list(self, lecture):
        """event should list speaker names in order"""
        # currently has one speaker
        assert lecture.speaker_list == "john lecturer"
        # add another speaker to the event
        speaker2 = Person.objects.create(first_name="sam", last_name="brown")
        Speaker.objects.create(event=lecture, person=speaker2)
        # order by last name, then first
        assert lecture.speaker_list == "sam brown, john lecturer"


class TestEventPage(WagtailPageTests):
    def test_subpages(self):
        """event page can't have children"""
        self.assertAllowedSubpageTypes(Event, [])

    def test_parent_pages(self):
        """event can only be created under projects link page"""
        self.assertAllowedParentPageTypes(Event, [EventsLinkPage])


class TestEventsLinkpage(WagtailPageTests):
    # skip because this is failing for no reason
    @pytest.mark.skip
    def test_subpages(self):
        """events link page only allowed child is event page"""
        self.assertAllowedSubpageTypes(EventsLinkPage, [Event, ContentPage, LinkPage])

    def test_parent_pages(self):
        """events link page should not be creatable in admin"""
        self.assertAllowedParentPageTypes(EventsLinkPage, [])
