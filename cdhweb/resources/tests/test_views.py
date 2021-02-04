import string
from datetime import timedelta
from unittest import skip

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from mezzanine.pages.models import Page
from mezzanine.core.models import CONTENT_STATUS_DRAFT
import pytest

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event, EventType
from cdhweb.projects.models import Project, GrantType, Grant
from cdhweb.resources.models import LandingPage
from cdhweb.resources.sitemaps import PageSitemap
from cdhweb.resources.utils import absolutize_url

@skip("fixme - move to pages")
class TestViews(TestCase):
    fixtures = ['test_pages.json']

    def test_child_pages_attachment(self):
        about = Page.objects.get(title='About')
        annual_report = Page.objects.get(title='Annual Report')
        response = self.client.get(about.get_absolute_url())
        # page-children attachment section should be present
        self.assertContains(
            response, '<div class="attachments page-children">')
        # child page title and url should be present
        self.assertContains(response, annual_report.title)
        self.assertContains(response, annual_report.get_absolute_url())

        # delete child page to check behavior without
        annual_report.delete()
        response = self.client.get(about.get_absolute_url())
        # should not error, should not contain page-children attachment section
        self.assertNotContains(
            response, '<div class="attachments page-children">')


@pytest.mark.django_db
def test_absolutize_url():
    https_url = 'https://example.com/some/path/'
    # https url is returned unchanged
    assert absolutize_url(https_url) == https_url
    # testing with default site domain
    current_site = Site.objects.get_current()

    # test site domain without https
    current_site.domain = 'example.org'
    current_site.save()
    local_path = '/foo/bar/'
    assert absolutize_url(local_path) == 'https://example.org/foo/bar/'
    # trailing slash in domain doesn't result in double slash
    current_site.domain = 'example.org/'
    current_site.save()
    assert absolutize_url(local_path) == 'https://example.org/foo/bar/'
    # site at subdomain should work too
    current_site.domain = 'example.org/sub/'
    current_site.save()
    assert absolutize_url(local_path) == 'https://example.org/sub/foo/bar/'
    # site with https:// included
    current_site.domain = 'https://example.org'
    assert absolutize_url(local_path) == 'https://example.org/sub/foo/bar/'
