import pytest
from wagtail.models import Site

from cdhweb.pages.utils import absolutize_url


@pytest.mark.django_db
def test_absolutize_url():
    https_url = "https://localhost/some/path/"
    # https url is returned unchanged
    assert absolutize_url(https_url) == https_url

    # now uses wagtail site, can't set root url here
    local_path = "/foo/bar/"
    assert absolutize_url(local_path) == "http://localhost/foo/bar/"
