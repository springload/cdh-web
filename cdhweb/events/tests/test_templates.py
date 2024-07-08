from django.template.defaultfilters import date
from django.urls import reverse
from django.utils.timezone import localtime
from pytest_django.asserts import assertContains, assertNotContains

from cdhweb.pages.models import PageIntro


class TestEventDetailTemplate:
    def test_event_title(self, client, workshop):
        """event detail page should include event title"""
        response = client.get(workshop.get_url())
        assertContains(response, "testing workshop")

    def test_event_content(self, client, workshop):
        """event detail page should include event content"""
        response = client.get(workshop.get_url())
        assertContains(response, "<p>Digital Mapping workshop for 2019</p>", html=True)

    def test_speakers(self, client, lecture):
        """event detail page should list info for all event speakers"""
        response = client.get(lecture.get_url())
        assertContains(response, "john lecturer")  # name
        assertContains(response, "princeton university")  # affiliation

    def test_event_type(self, client, workshop):
        """event detail page should include event type"""
        response = client.get(workshop.get_url())
        assertContains(response, "<p>Workshop</p>", html=True)

    def test_event_type_name(self, client, workshop):
        """event detail page shouldn't include type if same as title"""
        workshop.title = "Workshop"
        workshop.save()
        response = client.get(workshop.get_url())
        assertNotContains(response, "<p>Workshop</p>", html=True)

    def test_when(self, client, workshop):
        """event detail page should include date/time of event"""
        response = client.get(workshop.get_url())
        assertContains(response, "<div>%s</div>" % workshop.when(), html=True)

    def test_location(self, client, workshop):
        """event detail page should include location of event"""
        response = client.get(workshop.get_url())
        assertContains(
            response,
            '<span property="schema:name">Center for Digital Humanities</span>',
            html=True,
        )

    def test_address(self, client, workshop):
        """event detail page should include address for non-virtual event"""
        response = client.get(workshop.get_url())
        assertContains(
            response,
            '<div property="schema:address">Floor B, Firestone Library</div>',
            html=True,
        )

    def test_address(self, client, lecture):
        """event detail page should include join url for virtual event"""
        response = client.get(lecture.get_url())
        assertContains(response, "https://princeton.zoom.us/my/zoomroom")

    def test_address(self, client, workshop):
        """event detail page should include iCal export url"""
        response = client.get(workshop.get_url())
        assertContains(response, workshop.get_ical_url())


class TestEventArchiveTemplate:
    def test_title(self, client, events):
        """event archive page should display archive title"""
        # upcoming (default)
        response = client.get(reverse("events:upcoming"))
        assertContains(response, "<h1>Upcoming Events</h1>", html=True)
        # semester view
        response = client.get(
            reverse("events:by-semester", kwargs={"semester": "spring", "year": "2017"})
        )
        assertContains(response, "<h1>Spring 2017 Events</h1>", html=True)

    def test_no_events(self, db, client):
        """empty event archive page should display special message"""
        # filler message
        response = client.get(reverse("events:upcoming"))
        assertContains(response, "Next semester's events are being scheduled.")
        # no past events section
        assertNotContains(response, "<h2>Past Events</h2>", html=True)

    def test_past_events(self, client, events):
        """event archive page should list past events in special section"""
        response = client.get(reverse("events:upcoming"))
        assertContains(response, "<h2>Past Events</h2>", html=True)

    def test_event_titles(self, client, events):
        """event archive page should list event titles on cards"""
        response = client.get(reverse("events:upcoming"))
        for _, event in events.items():
            assertContains(response, event.title)

    def test_event_speakers(self, client, lecture):
        """event archive page should list event speakers on cards"""
        # lecture has one speaker
        response = client.get(reverse("events:upcoming"))
        assertContains(response, str(lecture.speakers.first().person))

    def test_event_date_time(self, client, workshop):
        """event archive page should list event date/time on cards"""
        response = client.get(reverse("events:upcoming"))
        # start/end dates (same month/day)
        assertContains(response, date(localtime(workshop.start_time), "F j"))
        assertContains(response, date(localtime(workshop.end_time), "j"))
        # start/end times (same day)
        assertContains(response, date(localtime(workshop.start_time), "g:i"))
        assertContains(response, date(localtime(workshop.end_time), "g:i A"))

    def test_event_location(self, client, workshop):
        """event archive page should list event location on cards"""
        response = client.get(reverse("events:upcoming"))
        assertContains(response, workshop.location.name)

    def test_event_location(self, client, workshop):
        """event archive page should list non-virtal event address on cards"""
        response = client.get(reverse("events:upcoming"))
        assertContains(response, workshop.location.address)
