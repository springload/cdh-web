from datetime import timedelta
from datetime import timezone as tz

import pytest
import pytz
from django.utils import timezone

from cdhweb.events.models import Event, EventsLinkPage, EventType, Location, Speaker
from cdhweb.pages.tests.conftest import to_streamfield_safe
from cdhweb.people.models import Person

EST = pytz.timezone("America/New_York")


def make_events_link_page(homepage):
    """Create a test events archive page underneath the homepage."""
    link = EventsLinkPage(title="events", link_url="events")
    homepage.add_child(instance=link)
    homepage.save()
    return link


def make_cdh_location():
    """Create the CDH, as an event location."""
    cdh = Location.objects.get_or_create(name="Center for Digital Humanities")[0]
    cdh.short_name = "CDH"
    cdh.address = "Floor B, Firestone Library"
    cdh.save()
    return cdh


def make_zoom_location():
    """Create a virtual event location for Zoom events."""
    zoom = Location.objects.get_or_create(name="Zoom Meeting")[0]
    zoom.short_name = "Zoom"
    zoom.is_virtual = True
    return zoom


def make_workshop(link_page, cdh_location):
    """Create a 2hr workshop at the CDH that happened in 2019."""
    workshop_type = EventType.objects.get_or_create(name="Workshop")[0]
    start_time = timezone.datetime(2019, 10, 5, 9, tzinfo=EST).astimezone(tz.utc)
    end_time = timezone.datetime(2019, 10, 5, 11, tzinfo=EST).astimezone(tz.utc)
    workshop = Event(
        title="testing workshop",
        body=to_streamfield_safe("<p>Digital Mapping workshop for 2019</p>"),
        start_time=start_time,
        end_time=end_time,
        location=cdh_location,
        type=workshop_type,
    )
    workshop.last_published_at = start_time - timedelta(days=10)
    link_page.add_child(instance=workshop)
    link_page.save()
    return workshop


def make_lecture(link_page, zoom_location):
    """Create a 1hr lecture on zoom with 1 speaker from 2018."""
    lecture_type = EventType.objects.get_or_create(name="Lecture")[0]
    start_time = timezone.datetime(2018, 4, 20, 16, 20, tzinfo=EST).astimezone(tz.utc)
    end_time = timezone.datetime(2018, 4, 20, 17, 20, tzinfo=EST).astimezone(tz.utc)
    lecture = Event(
        title="testing lecture",
        body=to_streamfield_safe(
            "<p>John Lecturer will discuss digital humanities on April 20th.</p>"
        ),
        start_time=start_time,
        end_time=end_time,
        location=zoom_location,
        type=lecture_type,
        join_url="https://princeton.zoom.us/my/zoomroom",
    )
    lecture.last_published_at = start_time - timedelta(days=10)
    link_page.add_child(instance=lecture)
    link_page.save()
    lecturer = Person.objects.create(
        first_name="john",
        last_name="lecturer",
        institution="princeton university",
    )
    Speaker.objects.create(person=lecturer, event=lecture)
    return lecture


def make_deadline(link_page):
    """Create a deadline set for 2099."""
    deadline_type = EventType.objects.get_or_create(name="Deadline")[0]
    start_time = timezone.datetime(2099, 1, 1, tzinfo=EST).astimezone(tz.utc)
    end_time = timezone.datetime(2099, 1, 1, tzinfo=EST).astimezone(tz.utc)
    deadline = Event(
        title="testing deadline",
        body=to_streamfield_safe("<p>An important due date in the far future!</p>"),
        start_time=start_time,
        end_time=end_time,
        type=deadline_type,
    )
    deadline.last_published_at = start_time - timedelta(days=10)
    link_page.add_child(instance=deadline)
    link_page.save()
    return deadline


def make_course(link_page):
    """Create a course that happened spring 2017."""
    course_type = EventType.objects.get_or_create(name="Course")[0]
    start_time = timezone.datetime(2017, 2, 2, tzinfo=EST).astimezone(tz.utc)
    end_time = timezone.datetime(2017, 4, 27, tzinfo=EST).astimezone(tz.utc)
    course = Event(
        title="testing course",
        body=to_streamfield_safe("<p>February 2017 Intro to Digital Humanities</p>"),
        start_time=start_time,
        end_time=end_time,
        type=course_type,
    )
    course.last_published_at = start_time - timedelta(days=10)
    link_page.add_child(instance=course)
    link_page.save()
    return course

def make_second_course():
    """Create a course that will happen in 2080. This second course is not defined
    as a fixture since it only needs to be called once."""
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

def make_events(link_page):
    """Create a variety of events and locations for testing."""
    cdh_location = make_cdh_location()
    zoom_location = make_zoom_location()
    return {
        "workshop": make_workshop(link_page, cdh_location),
        "lecture": make_lecture(link_page, zoom_location),
        "deadline": make_deadline(link_page),
        "course": make_course(link_page),
    }


@pytest.fixture
def events_link_page(db, homepage):
    return make_events_link_page(homepage)


@pytest.fixture
def cdh_location(db):
    return make_cdh_location()


@pytest.fixture
def zoom_location(db):
    return make_zoom_location()


@pytest.fixture
def workshop(db, events_link_page, cdh_location):
    return make_workshop(events_link_page, cdh_location)


@pytest.fixture
def lecture(db, events_link_page, zoom_location):
    return make_lecture(events_link_page, zoom_location)


@pytest.fixture
def deadline(db, events_link_page):
    return make_deadline(events_link_page)


@pytest.fixture
def course(db, events_link_page):
    return make_course(events_link_page)


@pytest.fixture
def events(db, workshop, lecture, deadline, course):
    return {
        "workshop": workshop,
        "lecture": lecture,
        "deadline": deadline,
        "course": course,
    }
