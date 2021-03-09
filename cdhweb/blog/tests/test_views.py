class TestBlogPostDetailView:

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
