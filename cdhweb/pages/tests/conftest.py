import json
from datetime import datetime
from operator import attrgetter
from unittest.mock import Mock

import pytest
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from wagtail.models import Page, Site

from cdhweb.pages.models import ContentPage, ExternalAttachment, HomePage, LandingPage
from cdhweb.pages.views import LastModifiedListMixin, LastModifiedMixin


def to_streamfield_safe(content):
    """Utility method used for exodus preserved for creating test fixtures.
    Creates a streamfield, but does no HTML validation and creates a block
    of type 'paragraph' instead of migrated."""
    return json.dumps([{"type": "paragraph", "value": content}])


def make_wagtail_site():
    """Ensure a single Wagtail site exists for testing."""
    return Site.objects.get()


def make_homepage(site):
    """Create a test homepage and set it as the root of the Wagtail site."""
    root = Page.objects.get(title="Root")
    home = HomePage(
        title="home",
        slug="",
        body=json.dumps(
            [{"type": "paragraph", "value": "<p>content of the home page</p>"}]
        ),
    )
    root.add_child(instance=home)
    root.save()
    site.root_page = home
    site.save()
    return home


def make_landing_page(homepage):
    """Create a test landing page."""
    landing = LandingPage(
        title="landing",
        slug="landing",
        tagline="tagline",
        body=json.dumps(
            [{"type": "paragraph", "value": "<p>content of the landing page</p>"}]
        ),
    )
    homepage.add_child(instance=landing)
    homepage.save()
    return landing


def make_content_page(landing_page):
    """Create a test content page."""
    content = ContentPage(
        title="content",
        slug="content",
        body=json.dumps(
            [{"type": "paragraph", "value": "<p>content of the content page</p>"}]
        ),
    )
    landing_page.add_child(instance=content)
    landing_page.save()
    return content


def make_attachment():
    """Create a testing external (link) attachment."""
    return ExternalAttachment.objects.create(
        title="Example Attachment",
        url="http://example.com/",
        author="Example Author",
    )


@pytest.fixture
def site(db):
    return make_wagtail_site()


@pytest.fixture
def homepage(db, site):
    return make_homepage(site)


@pytest.fixture
def landing_page(db, homepage):
    return make_landing_page(homepage)


@pytest.fixture
def content_page(db, landing_page):
    return make_content_page(landing_page)


@pytest.fixture
def attachment(db):
    return make_attachment()


class MyModel:
    # fake model with timestamp field for testing LastModified views
    def __init__(self, updated):
        self.updated = updated


class MyModelQuerySet:
    # fake queryset for testing LastModified views
    def __init__(self, objects):
        self.objects = objects

    def exists(self):
        return bool(self.objects)

    def order_by(self, key):
        self.objects.sort(key=attrgetter(key))
        return self

    def first(self):
        return self.objects[0]

    def reverse(self):
        self.objects.reverse()
        return self


class MyLastModifiedDetailView(LastModifiedMixin, DetailView):
    # fake view that uses LastModifiedMixin for testing
    template_name = ""


class MyLastModifiedListView(LastModifiedListMixin, ListView):
    # fake view that uses LastModifiedListMixin for testing
    template_name = ""


@pytest.fixture
def lmod_view():
    """create a testing LastModifiedDetailView for one object"""
    view = MyLastModifiedDetailView()
    view.get_object = Mock(return_value=MyModel(updated=timezone.now()))
    return view


@pytest.fixture
def lmod_objects():
    """a list of fake model objects with different timestamps"""
    return [
        MyModel(updated=timezone.make_aware(datetime(2017, 1, 1, 20, 5))),
        MyModel(updated=timezone.make_aware(datetime(1990, 5, 4, 2, 55))),
        MyModel(updated=timezone.now()),
    ]


@pytest.fixture
def lmod_list_view(lmod_objects):
    """create a testing LastModifiedListView with several timestamped objects"""
    view = MyLastModifiedListView()
    view.get_queryset = Mock(return_value=MyModelQuerySet(lmod_objects))
    return view
