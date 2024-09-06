import pytest
from django.test import RequestFactory
from wagtail.models import Site

from cdhweb.pages.templatetags import cdh_tags


def test_url_to_icon():
    assert cdh_tags.url_to_icon("/people/staff/") == "ppl"
    assert cdh_tags.url_to_icon("/projects/") == "folder"
    assert cdh_tags.url_to_icon("/events/") == "cal"
    assert cdh_tags.url_to_icon("/contact/") == "convo"
    assert cdh_tags.url_to_icon("/grants/seed-grant/") == "seed"
    assert cdh_tags.url_to_icon("/graduate-fellowships/") == "medal"
    assert cdh_tags.url_to_icon("/grants/") == "grant"
    assert cdh_tags.url_to_icon("/unknown/") == ""
    assert cdh_tags.url_to_icon("/year-of-data/") == "cal"
    assert cdh_tags.url_to_icon(None) == ""


@pytest.mark.django_db
def test_url_to_icon_path():
    current_site = Site.objects.order_by("is_default_site").first()

    assert (
        cdh_tags.url_to_icon_path("/people/staff/")
        == f"{current_site.root_url}/static/img/cdh-icons/png@2X/ppl@2x.png"
    )


def test_startswith():
    assert cdh_tags.startswith("yes", "y")
    assert not cdh_tags.startswith("no", "y")
    assert not cdh_tags.startswith(3, "y")


def test_url_replace():
    rf = RequestFactory()
    request = rf.get("/search?q=digital&page=2")
    context = {"request": request}
    assert cdh_tags.url_replace(context, "page", 3) == "q=digital&page=3"
