from datetime import timedelta

import pytest
from django.utils import timezone
from cdhweb.events.models import Event, EventType, EventsLinkPage, Location


@pytest.fixture
def events_link_page(db, homepage):
    """create a test events archive page underneath the homepage"""
    link = EventsLinkPage(title="events", link_url="events")
    homepage.add_child(instance=link)
    homepage.save()
    return link


@pytest.fixture
def workshop(db, events_link_page, cdh_location):
    """a 2hr workshop at the CDH that happened yesterday"""
    yesterday = timezone.now() - timedelta(days=1)
    workshop_type = EventType.objects.get_or_create(name="Workshop")[0]
    workshop = Event(
        title="testing workshop",
        content="my workshop description",
        start_time=yesterday,
        end_time=yesterday + timedelta(hours=2),
        location=cdh_location,
        type=workshop_type
    )
    events_link_page.add_child(instance=workshop)
    events_link_page.save()
    return workshop


@pytest.fixture
def lecture(db, events_link_page, zoom_location):
    """a 1hr lecture on zoom that happened a month ago with 1 speaker"""
    last_month = timezone.now() - timedelta(days=30)
    lecture_type = EventType.objects.get_or_create(name="Lecture")[0]
    lecture = Event(
        title="testing lecture",
        content="my lecture description",
        start_time=last_month,
        end_time=last_month + timedelta(hours=1),
        location=zoom_location,
        type=lecture_type,
    )
    events_link_page.add_child(instance=lecture)
    events_link_page.save()
    return lecture


@pytest.fixture
def deadline(db, events_link_page):
    """a deadline set for tomorrow"""
    tomorrow = timezone.now() + timedelta(days=1)
    deadline_type = EventType.objects.get_or_create(name="Deadline")[0]
    deadline = Event(
        title="testing deadline",
        content="my deadline description",
        start_time=tomorrow,
        end_time=tomorrow,
        type=deadline_type
    )
    events_link_page.add_child(instance=deadline)
    events_link_page.save()
    return deadline


@pytest.fixture
def cdh_location(db):
    """the CDH, as an event location"""
    cdh = Location.objects.get_or_create(
        name="Center for Digital Humanities")[0]
    cdh.short_name = "CDH"
    cdh.address = "Floor B, Firestone Library"
    cdh.save()
    return cdh


@pytest.fixture
def zoom_location(db):
    """virtual event location for Zoom events"""
    zoom = Location.objects.get_or_create(name="Zoom Meeting")[0]
    zoom.short_name = "Zoom"
    zoom.is_virtual = True
    return zoom


@pytest.fixture
def events(db, workshop, lecture, deadline):
    """convenience fixture to create several events and associated models"""
    return {
        "workshop": workshop,
        "lecture": lecture,
        "deadline": deadline,
    }
