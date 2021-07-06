from datetime import timedelta
from datetime import timezone as tz

import pytest
from django.utils import timezone


from cdhweb.events.models import Event, EventType, EventsLinkPage, Location, Speaker
from cdhweb.people.models import Person
from cdhweb.pages.tests.conftest import to_streamfield_safe


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
    """Create a 2hr workshop at the CDH that happened yesterday."""
    yesterday = timezone.now() - timedelta(days=1)
    workshop_type = EventType.objects.get_or_create(name="Workshop")[0]
    workshop = Event(
        title="testing workshop",
        body=to_streamfield_safe("<p>my workshop description</p>"),
        start_time=yesterday,
        end_time=yesterday + timedelta(hours=2),
        location=cdh_location,
        type=workshop_type,
    )
    link_page.add_child(instance=workshop)
    link_page.save()
    return workshop


def make_lecture(link_page, zoom_location):
    """Create a 1hr lecture on zoom that happened a month ago with 1 speaker."""
    last_month = timezone.now() - timedelta(days=30)
    lecture_type = EventType.objects.get_or_create(name="Lecture")[0]
    lecture = Event(
        title="testing lecture",
        body=to_streamfield_safe("<p>my lecture description</p>"),
        start_time=last_month,
        end_time=last_month + timedelta(hours=1),
        location=zoom_location,
        type=lecture_type,
        join_url="https://princeton.zoom.us/my/zoomroom",
    )
    link_page.add_child(instance=lecture)
    link_page.save()
    lecturer = Person.objects.create(
        first_name="john", last_name="lecturer", institution="princeton university"
    )
    Speaker.objects.create(person=lecturer, event=lecture)
    return lecture


def make_deadline(link_page):
    """Create a deadline set for tomorrow."""
    tomorrow = timezone.now() + timedelta(days=1)
    deadline_type = EventType.objects.get_or_create(name="Deadline")[0]
    deadline = Event(
        title="testing deadline",
        body=to_streamfield_safe("<p>my deadline description</p>"),
        start_time=tomorrow,
        end_time=tomorrow,
        type=deadline_type,
    )
    link_page.add_child(instance=deadline)
    link_page.save()
    return deadline


def make_course(link_page):
    """Create a course that happened spring 2017."""
    course_type = EventType.objects.get_or_create(name="Course")[0]
    course = Event(
        title="testing course",
        body=to_streamfield_safe("<p>my course description</p>"),
        start_time=timezone.datetime(2017, 2, 2, tzinfo=tz.utc),
        end_time=timezone.datetime(2017, 4, 27, tzinfo=tz.utc),
        type=course_type,
    )
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
