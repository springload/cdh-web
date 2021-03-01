import json

import pytest
from wagtail.core.models import Page, Site

from cdhweb.pages.models import ContentPage, HomePage, LandingPage


@pytest.fixture
def site(db):
    """Ensure a single Wagtail site exists for testing."""
    return Site.objects.get()


@pytest.fixture
def homepage(db, site):
    """Create a test homepage and set it as the root of the Wagtail site."""
    root = Page.objects.get(title="Root")
    home = HomePage(title="home", slug="",
                    body=json.dumps([{
                        "type": "paragraph",
                        "value": "<p>content of the home page</p>"
                    }]))
    root.add_child(instance=home)
    root.save()
    site.root_page = home
    site.save()
    return home


@pytest.fixture
def landing_page(db, homepage):
    """Create a test landing page."""
    landing = LandingPage(title="landing", slug="landing", tagline="tagline",
                          body=json.dumps([{
                              "type": "paragraph",
                              "value": "<p>content of the landing page</p>"
                          }]))
    homepage.add_child(instance=landing)
    homepage.save()
    return landing


@pytest.fixture
def content_page(db, landing_page):
    """Create a test content page."""
    content = ContentPage(title="content", slug="content",
                          body=json.dumps([{
                              "type": "paragraph",
                              "value": "<p>content of the content page</p>"
                          }]))
    landing_page.add_child(instance=content)
    landing_page.save()
    return content
