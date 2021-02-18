# -*- coding: utf-8 -*-
from unittest import skip
from datetime import datetime, timedelta

import icalendar
import pytest
import pytz
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mezzanine.core.models import CONTENT_STATUS_DRAFT
from mezzanine.pages.models import RichTextPage

from cdhweb.events.models import Event, EventType, Location
from cdhweb.people.models import Person
from cdhweb.resources.utils import absolutize_url


@pytest.mark.skip
class TestViews(TestCase):
    fixtures = ['test_events.json']

    def test_event_ical(self):
        jan15 = datetime(2015, 1, 15, hour=16,
                         tzinfo=timezone.get_default_timezone())  # make timezone aware
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
        assert cal.subcomponents[0]['uid'] == absolutize_url(
            event.get_absolute_url())

    def test_redirect(self):
        # valid id gives permanent redirect to slug url
        event = Event.objects.first()
        url = reverse('event:by-id', kwargs={'pk': event.pk})
        response = self.client.get(url)
        assert response.status_code == 301
        assert response.url == event.get_absolute_url()

        # bogus id returns a 404
        url = reverse('event:by-id', kwargs={'pk': 45})
        response = self.client.get(url)
        assert response.status_code == 404

    def test_event_detail(self):
        event = Event.objects.first()
        response = self.client.get(event.get_absolute_url())
        # content that should appear somewhere
        self.assertContains(response, event.title)
        self.assertContains(response, event.event_type)
        self.assertContains(response, event.location.name)
        self.assertContains(response, event.location.address)
        self.assertContains(response, event.when())
        self.assertContains(response, event.get_ical_url())
        self.assertContains(response, event.full_url())
        self.assertContains(response, event.content)
        self.assertNotContains(response, '<img property="schema:image',
                               msg_prefix='should not embed image when event has none')

        # last modified header should be set on response
        assert response.has_header('last-modified')
        modified = event.updated.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert response['Last-Modified'] == modified
        # and should return 304 not modified when header is present
        response = self.client.get(event.get_absolute_url(),
                                   HTTP_IF_MODIFIED_SINCE=modified)
        assert response.status_code == 304

        # test with user without profile
        speaker = Person.objects.create(username='anon', first_name='Anne',
                                        last_name='Onomus')
        event.speakers.add(speaker)
        response = self.client.get(event.get_absolute_url())
        self.assertContains(response, str(speaker),
                            msg_prefix='event speaker name should display without profile')

        # test usage of virtual URL
        zoom, _ = Location.objects.get_or_create(name="Zoom", is_virtual=True)
        event.join_url = "princeton.zoom.us/my/zoomroom"
        event.location = zoom
        event.save()
        response = self.client.get(event.get_absolute_url())
        self.assertContains(response, "princeton.zoom.us/my/zoomroom")

        # TODO: how to test with image associated?

        # get by slug with wrong dates - should not be found
        response = self.client.get(reverse('event:detail',
                                           args=[1999, '01', event.slug]))
        assert response.status_code == 404

        # set status to draft
        event.status = CONTENT_STATUS_DRAFT
        event.save()
        response = self.client.get(event.get_absolute_url())
        assert response.status_code == 404

    def test_upcoming(self):
        # no upcoming events - should not error
        response = self.client.get(reverse('event:upcoming'))
        assert response.status_code == 200
        self.assertContains(response,
                            "Next semester's events are being scheduled")
        self.assertContains(response,
                            "Check back later")
        self.assertContains(response,
                            reverse('event:by-semester', args=['fall', '2017']))

        # use django timezone util for timezone-aware datetime
        tomorrow = timezone.now() + timedelta(days=1)
        event_type = EventType.objects.first()
        next_event = Event.objects.create(start_time=tomorrow, end_time=tomorrow,
                                          slug='some-workshop', event_type=event_type,
                                          title='A workshop')
        today = timezone.now()
        earlier_today = datetime(today.year, today.month, today.day,
                                 tzinfo=timezone.get_default_timezone())
        earlier_event = Event.objects.create(start_time=earlier_today,
                                             end_time=earlier_today +
                                             timedelta(hours=1),
                                             slug='another-workshop', event_type=event_type,
                                             title='Earlier workshop')

        response = self.client.get(reverse('event:upcoming'))
        assert next_event in response.context['events']
        assert earlier_event in response.context['events']
        # summary fields that should be in list view
        self.assertContains(response, next_event.title)
        self.assertContains(response, next_event.get_absolute_url())
        # (not testing all fields)

        # test usage of virtual URL for upcoming event
        zoom, _ = Location.objects.get_or_create(name="Zoom", is_virtual=True)
        next_event.join_url = "princeton.zoom.us/my/zoomroom"
        next_event.location = zoom
        next_event.save()
        response = self.client.get(reverse('event:upcoming'))
        self.assertContains(response, "princeton.zoom.us/my/zoomroom")

        # should not include past events
        past_event = Event.objects.filter(end_time__lte=today).first()
        assert past_event not in response.context['events']

        # should include recent events
        assert past_event in response.context['past']
        self.assertContains(response, 'Past Events')
        self.assertContains(response, past_event.title)
        self.assertContains(response, past_event.get_absolute_url())

        # should include all semesters and years represented in events
        date_list = response.context['date_list']
        assert ('Fall', 2016) in date_list
        assert ('Spring', 2017) in date_list
        assert ('Fall', 2017) in date_list

        # should link to events by semester
        for semester, year in date_list:
            self.assertContains(response,
                                reverse('event:by-semester', args=[semester.lower(), year]))

        # last modified header should be set on response
        assert response.has_header('last-modified')
        modified = Event.objects.upcoming().order_by('updated').first().updated
        modified = modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
        assert response['Last-Modified'] == modified
        # and should return 304 not modified when header is present
        response = self.client.get(reverse('event:upcoming'),
                                   HTTP_IF_MODIFIED_SINCE=modified)
        assert response.status_code == 304

        # no upcoming events OR past events
        Event.objects.all().delete()
        response = self.client.get(reverse('event:upcoming'))
        assert response.status_code == 200
        self.assertContains(response,
                            "Next semester's events are being scheduled")
        self.assertContains(response,
                            "Check back later.")

        # should include blurb if there is a matching page in hierarchy
        page = RichTextPage(title='Events')  # should have slug 'events'
        page.content = 'An event blurb'
        page.save()
        response = self.client.get(reverse('event:upcoming'))
        self.assertContains(response, 'An event blurb')

        # should skip blurb if content is empty
        page.content = '<p>&nbsp;&nbsp;</p>'
        page.save()
        response = self.client.get(reverse('event:upcoming'))
        self.assertNotContains(response, '&nbsp;&nbsp')

    def test_events_by_semester(self):
        response = self.client.get(
            reverse('event:by-semester', args=['spring', 2017]))
        assert response.context['title'] == 'Spring 2017'
        self.assertContains(response, 'Spring 2017 Events')
        self.assertContains(response, reverse('event:upcoming'))

        events = Event.objects.filter(
            start_time__year=2017, start_time__month__lte=5)
        for evt in events:
            assert evt in response.context['object_list']
            self.assertContains(response, evt.title)
            self.assertContains(response, evt.event_type.name)

        date_list = response.context['date_list']
        assert ('Fall', 2016) in date_list
        assert ('Spring', 2017) in date_list
        assert ('Fall', 2017) in date_list

        # should link to events by semester
        for semester, year in date_list:
            self.assertContains(response,
                                reverse('event:by-semester', args=[semester.lower(), year]))
