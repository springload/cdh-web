import pytest
from django.urls import reverse

from cdhweb.blog.sitemaps import BlogListSitemap


class TestBlogListSitemap:
    @pytest.mark.django_db
    def test_items(self, announcement):
        items = BlogListSitemap().items()
        # expect three: list, year, year+month
        assert len(items) == 3

        assert ("list",) in items
        assert (announcement.first_published_at.year,) in items
        assert (
            announcement.first_published_at.year,
            announcement.first_published_at.month,
        ) in items

    def test_location(self):
        # named url
        assert BlogListSitemap().location(("list",)) == reverse("blog:list")
        # year only
        assert BlogListSitemap().location((2020,)) == reverse(
            "blog:by-year", args=[2020]
        )
        # year + month; requires two-digit month
        assert BlogListSitemap().location((2019, 3)) == reverse(
            "blog:by-month", args=[2019, "03"]
        )

    @pytest.mark.django_db
    def test_lastmod(self, announcement, article):
        # announcement fixture published yesterday, most recent for list
        blogsitemap = BlogListSitemap()
        assert blogsitemap.lastmod(("list",)) == announcement.first_published_at

        assert (
            blogsitemap.lastmod((article.first_published_at.year,))
            == article.first_published_at
        )

        assert (
            blogsitemap.lastmod(
                (article.first_published_at.year, article.first_published_at.month)
            )
            == article.first_published_at
        )

    @pytest.mark.django_db
    def test_get(self, client, announcement):
        # test that it actually renders, to catch any other problems
        resp = client.get("/sitemap-blog.xml")
        assert resp.status_code == 200
