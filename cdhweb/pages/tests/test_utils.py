import pytest
from django.contrib.sites.models import Site

from cdhweb.pages.utils import absolutize_url


@pytest.mark.django_db
def test_absolutize_url():
    https_url = "https://example.com/some/path/"
    # https url is returned unchanged
    assert absolutize_url(https_url) == https_url
    # testing with default site domain
    current_site = Site.objects.get_current()

    # test site domain without https
    current_site.domain = "example.org"
    current_site.save()
    local_path = "/foo/bar/"
    assert absolutize_url(local_path) == "https://example.org/foo/bar/"
    # trailing slash in domain doesn't result in double slash
    current_site.domain = "example.org/"
    current_site.save()
    assert absolutize_url(local_path) == "https://example.org/foo/bar/"
    # site at subdomain should work too
    current_site.domain = "example.org/sub/"
    current_site.save()
    assert absolutize_url(local_path) == "https://example.org/sub/foo/bar/"
    # site with https:// included
    current_site.domain = "https://example.org"
    assert absolutize_url(local_path) == "https://example.org/sub/foo/bar/"
