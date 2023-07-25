from pytest_django.asserts import assertContains


class TestBlogPostDetail:
    def test_title(self, client, announcement):
        """blog post detail page should include post title"""
        response = client.get(announcement.get_url())
        assertContains(
            response,
            '<h1 property="schema:headline">A Big Announcement!</h1>',
            html=True,
        )

    def test_body(self, client, announcement):
        """blog post detail page should include post body"""
        response = client.get(announcement.get_url())
        assertContains(
            response,
            "<p>We're making a big digital humanities announcement.</p>",
            html=True,
        )

    def test_authors(self, site, client, article, staffer_profile):
        """blog post detail page should list author names and link to profiles"""
        response = client.get(article.get_url())
        # list names for both authors
        assertContains(
            response, '<span property="schema:name">Staffer</span>', html=True
        )
        assertContains(
            response, '<span property="schema:name">Postdoc</span>', html=True
        )
        # profile URL for staffer
        assertContains(response, staffer_profile.get_url())

    def test_pubdate(self, client, article):
        """blog post detail page should list post publication date"""
        response = client.get(article.get_url())
        assertContains(
            response, '<span class="date-published">March 4, 2019</span>', html=True
        )

    def test_next_prev(self, client, blog_posts):
        """blog post detail page should have next/prev post links"""
        announcement = blog_posts["announcement"]
        feature = blog_posts["project_feature"]
        article = blog_posts["article"]
        response = client.get(article.get_url())
        assertContains(
            response,
            '<a rel="prev" href="%s">%s</a>' % (feature.get_url(), feature.title),
            html=True,
        )
        assertContains(
            response,
            '<a rel="next" href="%s">%s</a>'
            % (announcement.get_url(), announcement.title),
            html=True,
        )

    def test_head_meta(self, client, article, staffer_profile):
        """blog post detail page should have meta tags in head"""
        response = client.get(article.get_url())
        # first published in 2019; in GMT
        assertContains(
            response,
            '<meta name="article.published_time" content="%s">'
            % article.first_published_at.isoformat(),
            html=True,
        )
        # most recently published/modified in 2020; in GMT
        assertContains(
            response,
            '<meta name="article.modified_time" content="%s">'
            % article.last_published_at.isoformat(),
            html=True,
        )
        # profile URL for staffer (postdoc doesn't have profile)
        assertContains(
            response,
            '<meta name="article.author" content="%s"/>' % staffer_profile.get_url(),
            html=True,
        )
