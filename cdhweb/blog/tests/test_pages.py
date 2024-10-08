import pytest
from wagtail.test.utils import WagtailPageTestCase

from cdhweb.blog.models import BlogLandingPage, BlogLinkPageArchived, BlogPost


class TestBlogPost:
    def test_short_title(self, article):
        """blog post should truncate title to 65char with ellipsis"""
        # article fixture has a long title
        assert article.short_title == "We wrote an article together for the CDH website"

    def test_author_list(self, article, staffer, postdoc):
        """blog post should list author names in order"""
        # article fixture has multiple authors
        assert article.authors.all()[0].person == staffer
        assert article.authors.all()[1].person == postdoc
        # reorder manually to check new ordering
        a1, a2 = article.authors.all()
        a1.sort_order = 2
        a1.save()
        a2.sort_order = 1
        a2.save()
        assert article.authors.all()[0].person == postdoc
        assert article.authors.all()[1].person == staffer

    def test_str(self, article):
        """blog post should display as title"""
        assert (
            str(article)
            == "We wrote an article together, and it got published on the CDH website"
        )

    @pytest.mark.skip("updated logic; test get_url_parts?")
    def test_get_url(self, article):
        """blog post should be accessed via custom url with y/m/d info"""
        # should pad with zeroes and include year, month, day, slug
        assert article.get_url() == "/updates/2019/03/04/%s/" % article.slug

    def test_sitemap(self, rf, article):
        """blog post should have increased priority in sitemap if featured"""
        # post that's not featured doesn't set priority (default is 0.5)
        request = rf.get(article.get_url())
        sitemap_urls = article.get_sitemap_urls(request=request)
        assert "priority" not in sitemap_urls[0]
        # featured post gets slightly increased priority (0.6)
        article.featured = True
        article.save()
        request = rf.get(article.get_url())
        sitemap_urls = article.get_sitemap_urls(request=request)
        assert sitemap_urls[0]["priority"] == 0.6


class TestBlogPostPage(WagtailPageTestCase):
    def test_subpage_types(self):
        """blog posts can't have children"""
        self.assertAllowedSubpageTypes(BlogPost, [])

    def test_parent_page_types(self):
        """blog posts always go under the blog link page"""
        self.assertAllowedParentPageTypes(
            BlogPost, [BlogLinkPageArchived, BlogLandingPage]
        )


class TestBlogLinkPageArchived(WagtailPageTestCase):
    def test_subpage_types(self):
        """only allowed child of blog link page is blogpost"""
        self.assertAllowedSubpageTypes(BlogLinkPageArchived, [BlogPost])

    def test_parent_page_types(self):
        """blog link page can't be created in admin"""
        self.assertAllowedParentPageTypes(BlogLinkPageArchived, [])
