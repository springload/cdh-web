import pytest
from django.urls import reverse

from cdhweb.events import views
from cdhweb.events.sitemaps import EventListSitemap


class TestEventListSitemap:
    @pytest.mark.django_db
    def test_items(self, deadline):
        semester_dates = views.EventSemesterDates().get_semester_date_list()

        items = EventListSitemap().items()
        # expect one for each semester date plus upcoming
        assert len(items) == len(semester_dates) + 1

        urls = [i[0] for i in items]
        url_views = [i[1] for i in items]

        assert reverse("events:upcoming") in urls
        # views should be instantiated, since semester archive needs args
        assert isinstance(url_views[0], views.UpcomingEventsView)
        assert isinstance(url_views[1], views.EventSemesterArchiveView)

    def test_location(self):
        loc = reverse("events:upcoming")
        # location is returned as is
        assert EventListSitemap().location((loc,)) == loc

    @pytest.mark.django_db
    def test_lastmod(self, deadline):
        # fixture to ensure we have at least one upcoming event
        assert (
            EventListSitemap().lastmod(("upcoming", views.UpcomingEventsView()))
            == views.UpcomingEventsView().last_modified()
        )

    @pytest.mark.django_db
    def test_get(self, client):
        # test that it actually renders, to catch any other problems
        resp = client.get("/sitemap-events.xml")
        assert resp.status_code == 200
