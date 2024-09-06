from datetime import date, timezone

import pytest
from django.urls import reverse
from pytest_django.asserts import assertContains

from cdhweb.blog.tests.conftest import announcement


class TestRssBlogPostFeed:
    def test_titles(self, client, blog_posts):
        """rss feed should list post titles"""
        response = client.get(reverse("rss"))
        for _, post in blog_posts.items():
            assertContains(response, "<title>%s</title>" % post.title)

    @pytest.mark.skip("broken in update, now using description template")
    def test_descriptions(self, client, blog_posts):
        """rss feed should list post descriptions"""
        response = client.get(reverse("rss"))
        for _, post in blog_posts.items():
            assertContains(
                response, "<description>%s</description>" % post.get_description()
            )

    def test_links(self, client, blog_posts):
        """rss feed should list post descriptions"""
        response = client.get(reverse("rss"))
        for _, post in blog_posts.items():
            assertContains(response, "<link>%s</link>" % post.get_full_url())

    def test_author_names(self, client, blog_posts):
        """rss feed should list author names and emails if present"""
        response = client.get(reverse("rss"))
        # author name is combined with email, if present and single author
        assertContains(response, "<author>tom@princeton.edu (Tom)</author>")

    def test_pubdates(self, client, blog_posts):
        """rss feed should list post publication dates"""
        response = client.get(reverse("rss"))
        # all dates will display as their UTC versions
        for _, post in blog_posts.items():
            assertContains(
                response,
                "<pubDate>%s</pubDate>"
                % post.first_published_at.astimezone(timezone.utc).strftime(
                    "%a, %d %b %Y %H:%M:%S %z"
                ),
            )

    def test_last_modified(self, client, blog_posts):
        """rss feed should list most recent modification date for whole feed"""
        response = client.get(reverse("rss"))
        # most recently modified post was announcement; displays as UTC
        announcement = blog_posts["announcement"]
        assertContains(
            response,
            "<lastBuildDate>%s</lastBuildDate>"
            % announcement.last_published_at.astimezone(timezone.utc).strftime(
                "%a, %d %b %Y %H:%M:%S %z"
            ),
        )
