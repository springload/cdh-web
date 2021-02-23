# -*- coding: utf-8 -*-
from datetime import timedelta
from unittest.mock import patch

import icalendar
import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains
from wagtail.core.models import Page


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


class TestEventRedirectView:

    def test_redirect_by_id(self, client, workshop):
        """should permanently redirect to new date/slug url via 301"""
        url = reverse("events:by-id", kwargs={"pk": workshop.pk})
        response = client.get(url)
        assert response.status_code == 301
        assert response.url == workshop.get_full_url()

    def test_invalid_id(self, client, workshop):
        """should return a 404 for nonexistent event ids"""
        url = reverse("events:by-id", kwargs={"pk": 45})
        response = client.get(url)
        assert response.status_code == 404


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

    @pytest.mark.skip("todo")
    def test_semester_dates(self, client, events):
        """should create list of all semesters for linking to views"""
        response = client.get(reverse("events:upcoming"))
        assert response.context["date_list"]

    def test_last_modified(self, client, events):
        """should send last modified date with response"""
        # set last updated date on one event to most recent
        workshop = events["workshop"]
        workshop.updated = timezone.now() + timedelta(days=1)
        workshop.save()
        # most recent modified date will appear as response header
        response = client.get(reverse("events:upcoming"))
        lmod = workshop.updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        assert response["Last-Modified"] == lmod

    def test_not_modified(self, client, events):
        """should serve 304 if event has not been modified"""
        # request using current last mod date; should report unchanged
        lmod = events["workshop"].updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = client.get(reverse("events:upcoming"),
                              HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304

    def test_head(self, client, events):
        """should respond to http HEAD request to check for modification"""
        # request using current last mod date; should report unchanged
        lmod = events["workshop"].updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
        response = client.get(reverse("events:upcoming"),
                              HTTP_IF_MODIFIED_SINCE=lmod)
        assert response.status_code == 304


class TestEventSemesterArchiveView:

    def test_no_events(self, db, client):
        """should 404 if no events for requested semester"""
        response = client.get(
            reverse("events:by-semester", args=["spring", 2099]))
        assert response.status_code == 404

    @pytest.mark.skip("todo")
    def test_event_archive(self, client, events):
        """should display all past events from requested semester"""
        # workshop was this semester; other events not shown
        response = client.get(
            reverse("events:by-semester", args=["spring", 2099]))
        assert events["workshop"] in response.context["events"]
        assert events["deadline"] not in response.context["events"]
        assert events["lecture"] not in response.context["events"]
