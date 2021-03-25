from django.urls import reverse
import pytest

from cdhweb.people import views
from cdhweb.people.sitemaps import PeopleListSitemap


class TestPeopleListSitemap:

    def test_items(self):
        items = PeopleListSitemap().items()
        url_names = [i[0] for i in items]
        url_views = [i[1] for i in items]

        for url_name in ['staff', 'students', 'affiliates', 'exec-committee']:
            assert url_name in url_names

        for view in [views.StaffListView, views.StudentListView,
                     views.AffiliateListView, views.ExecListView]:
            assert view in url_views

    def test_location(self):
        assert PeopleListSitemap().location(('staff',)) \
            == reverse('people:staff')

    @pytest.mark.django_db
    def test_lastmod(self, staffer):
        # fixture to ensure we have at least one record with a date
        assert PeopleListSitemap().lastmod(('staff', views.StaffListView)) ==\
            views.StaffListView().last_modified()

    @pytest.mark.django_db
    def test_get(self, client):
        # test that it actually renders, to catch any other problems
        resp = client.get('/sitemap-people.xml')
        assert resp.status_code == 200
