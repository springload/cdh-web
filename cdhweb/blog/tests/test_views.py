from datetime import date
from django.urls import reverse


class TestBlogYearArchiveView:

    def test_month_list(self, client, blog_posts):
        """blog post year archive should add months for all posts to context"""
        # year is irrelevant; we always want all months to render the dropdown
        response = client.get(reverse("blog:by-year", kwargs={"year": "2019"}))
        dates = [post.first_published_at for _title,
                 post in blog_posts.items()]
        # months will appear as datetime.date objects with day set to 1
        months = [date(pubdate.year, pubdate.month, 1) for pubdate in dates]
        # should be ordered with most recent first
        assert list(response.context["date_list"]) == \
            sorted(months, reverse=True)

    def test_title(self, client, blog_posts):
        """blog post year archive should add year to context as title"""
        response = client.get(reverse("blog:by-year", kwargs={"year": "2019"}))
        assert response.context["title"] == "2019"


class TestBlogMonthArchiveView:

    def test_month_list(self, client, blog_posts):
        """blog post year archive should add months for all posts to context"""
        # args are irrelevant; we always want all months to render the dropdown
        response = client.get(reverse("blog:by-month",
                              kwargs={"year": "2019", "month": "03"}))
        dates = [post.first_published_at for _title,
                 post in blog_posts.items()]
        # months will appear as datetime.date objects with day set to 1
        months = [date(pubdate.year, pubdate.month, 1) for pubdate in dates]
        # should be ordered with most recent first
        assert list(response.context["date_list"]) == \
            sorted(months, reverse=True)

    def test_title(self, client, blog_posts):
        """blog post year archive should add year/month to context as title"""
        response = client.get(reverse("blog:by-month",
                              kwargs={"year": "2019", "month": "03"}))
        assert response.context["title"] == "March 2019"


class TestBlogPostDetailView:

    def test_context_obj(self, client, announcement):
        """blog post detail view should serve blog post in context"""
        response = client.get(announcement.get_url())
        assert response.context["post"] == announcement

    def test_draft_404(self, client, announcement):
        """blog post detail view should serve 404 for draft posts"""
        announcement.unpublish()
        response = client.get(announcement.get_url())
        assert response.status_code == 404

    def test_next_prev(self, client, blog_posts):
        """blog post detail view should have next/prev posts in context"""
        article = blog_posts["article"]
        feature = blog_posts["project_feature"]
        announcement = blog_posts["announcement"]
        # article is oldest post; should have no prev and only next
        response = client.get(article.get_url())
        assert response.context["previous"] == None
        assert response.context["next"] == feature
        # feature is in the middle; should have prev and next
        response = client.get(feature.get_url())
        assert response.context["previous"] == article
        assert response.context["next"] == announcement
        # announcement is newest; should have prev but no next
        response = client.get(announcement.get_url())
        assert response.context["previous"] == feature
        assert response.context["next"] == None
