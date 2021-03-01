# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

import icalendar
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains
from wagtail.core.models import Page

from cdhweb.events.models import Event
from cdhweb.events.views import EventSemesterDates


class TestEventDetailView:

    def test_url(self, client, workshop):
        """should serve event via custom url with year, month and slug"""
        # check that year, month, and slug are in URL
        page_url = workshop.get_url()
        assert str(workshop.start_time.year) in page_url
        assert "%02d" % workshop.start_time.month in page_url
        assert workshop.slug in page_url

        # make a request; should delegate to wagtail's serve()
        try:
            with patch.object(Page, "serve") as page_serve:
                client.get(workshop.get_url())
        except:
            pass
        page_serve.assert_called_once()

    def test_draft(self, client, workshop):
        """should serve 404 for events that are not yet live"""
        # unpublish; should 404
        workshop.unpublish()
        response = client.get(workshop.get_url())
        assert response.status_code == 404

    def test_last_modified(self, client, workshop):
        """should send last modified date with response"""
        # last modified date will appear as response header
        response = client.get(workshop.get_url())
        lmod = workshop.updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        assert response["Last-Modified"] == lmod

    def test_not_modified(self, client, workshop):
        """should serve 304 if event has not been modified"""
        # request using current last mod date; should report unchanged
        lmod = workshop.updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = client.get(workshop.get_url(), HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304

    def test_head(self, client, workshop):
        """should respond to http HEAD request to check for modification"""
        # request using current last mod date; should report unchanged
        lmod = workshop.updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = client.head(workshop.get_url(), HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304


class TestEventIcalView:

    def test_ical_response(self, client, workshop):
        """should create iCalendar format file from event"""
        response = client.get(workshop.get_ical_url())
        assert response["Content-Type"] == "text/calendar"
        assert response["Content-Disposition"] == \
            'attachment; filename="%s.ics"' % workshop.slug
        # parsable as ical calendar
        cal = icalendar.Calendar.from_ical(response.content)
        # includes the requested event
        assert cal.subcomponents[0]["uid"] == workshop.get_full_url()


class TestUpcomingEventsView:

    def test_no_events(self, db, client):
        """should display message and not error if no events"""
        response = client.get(reverse("events:upcoming"))
        assert response.status_code == 200
        assertContains(response, "Check back later")

    def test_upcoming_events(self, client, events):
        """should display all upcoming events"""
        # deadline is upcoming; other events are past
        response = client.get(reverse("events:upcoming"))
        assert events["deadline"] in response.context["events"]
        assert events["workshop"] not in response.context["events"]
        assert events["lecture"] not in response.context["events"]

    def test_semester_dates(self, client, events):
        """should create list of all semesters for linking to views"""
        response = client.get(reverse("events:upcoming"))
        assert response.context["date_list"]

    def test_last_modified(self, client, events):
        """should send last modified date with response"""
        # get last modified date for most recent event
        most_recent = Event.objects.order_by("-updated").first()
        lmod = most_recent.updated.replace(microsecond=0) \
                          .strftime("%a, %d %b %Y %H:%M:%S GMT")
        # most recent modified date will appear as response header
        response = client.get(reverse("events:upcoming"))
        assert response["Last-Modified"] == lmod

    def test_not_modified(self, client, events):
        """should serve 304 if event has not been modified"""
        # get last modified date for most recent event
        most_recent = Event.objects.order_by("-updated").first()
        lmod = most_recent.updated.replace(microsecond=0) \
                          .strftime("%a, %d %b %Y %H:%M:%S GMT")
        # request using most recent mod date; should report unchanged
        response = client.get(reverse("events:upcoming"),
                              HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304

    def test_head(self, client, events):
        """should respond to http HEAD request to check for modification"""
        # request using current last mod date; should report unchanged
        most_recent = Event.objects.order_by("-updated").first()
        lmod = most_recent.updated.replace(microsecond=0) \
                          .strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = client.head(reverse("events:upcoming"),
                               HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304


class TestEventSemesterArchiveView:

    def test_no_events(self, db, client):
        """should 404 if no events for requested semester"""
        response = client.get(
            reverse("events:by-semester", args=["spring", 2099]))
        assert response.status_code == 404

    def test_event_archive(self, client, events):
        """should display all events from requested semester"""
        # all events were this semester except the course from 2017
        now = timezone.now()
        this_semester = EventSemesterDates.get_semester(now).lower()
        response = client.get(
            reverse("events:by-semester", args=[this_semester, now.year]))
        assert events["workshop"] in response.context["events"]
        assert events["lecture"] in response.context["events"]
        assert events["deadline"] in response.context["events"]
        assert events["course"] not in response.context["events"]
        # request spring 2017 only; should see course
        response = client.get(
            reverse("events:by-semester", args=["spring", 2017]))
        assert events["course"] in response.context["events"]
        assert events["workshop"] not in response.context["events"]
        assert events["lecture"] not in response.context["events"]
        assert events["deadline"] not in response.context["events"]
