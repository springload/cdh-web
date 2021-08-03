import pytest
from django.urls import reverse

from cdhweb.projects import views
from cdhweb.projects.sitemaps import ProjectListSitemap


class TestProjectListSitemap:
    def test_items(self):
        items = ProjectListSitemap().items()
        url_names = [i[0] for i in items]
        url_views = [i[1] for i in items]

        for url_name in ["sponsored", "staff", "working-groups"]:
            assert url_name in url_names

        for view in [
            views.SponsoredProjectListView,
            views.StaffProjectListView,
            views.WorkingGroupListView,
        ]:
            assert view in url_views

    def test_location(self):
        assert ProjectListSitemap().location(("staff",)) == reverse("projects:staff")

    @pytest.mark.django_db
    def test_lastmod(self, derrida):
        # fixture to ensure we have at least one record with a date
        assert (
            ProjectListSitemap().lastmod(("staff", views.StaffProjectListView))
            == views.StaffProjectListView().last_modified()
        )

    @pytest.mark.django_db
    def test_get(self, client):
        # test that it actually renders, to catch any other problems
        resp = client.get("/sitemap-projects.xml")
        assert resp.status_code == 200
