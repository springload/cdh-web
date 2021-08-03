from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import nested_form_data, rich_text, streamfield

from cdhweb.pages.models import ContentPage, HomePage, LandingPage


class TestHomePage(WagtailPageTests):
    def test_can_create(self):
        """should be able to create homepage at root"""
        self.assertCanCreateAt(
            Page,
            HomePage,
            nested_form_data(
                {
                    "title": "Home 2",
                    "slug": "home-2",
                    "body": streamfield(
                        [
                            ("paragraph", rich_text("homepage body text")),
                        ]
                    ),
                }
            ),
        )

    def test_parent_pages(self):
        """only allowed parent page type for homepage should be root"""
        self.assertAllowedParentPageTypes(HomePage, [Page])

    def test_subpages(self):
        """allowed subpage types for homepage should be landing and content"""
        self.assertAllowedSubpageTypes(HomePage, [LandingPage, ContentPage])


class TestLandingPage(WagtailPageTests):
    def test_can_create(self):
        """should be able to create landing page under homepage"""
        self.assertCanCreateAt(
            HomePage,
            LandingPage,
            nested_form_data(
                {
                    "title": "Engage",
                    "slug": "engage",
                    "tagline": "Consult, collaborate, and work with us",
                    "body": streamfield(
                        [
                            ("paragraph", rich_text("engage page text")),
                        ]
                    ),
                }
            ),
        )

    def test_parent_pages(self):
        """only allowed parent of landingpage should be home"""
        self.assertAllowedParentPageTypes(LandingPage, [HomePage])

    def test_subpages(self):
        """only allowed child page of landingpage should be contentpage"""
        self.assertAllowedSubpageTypes(LandingPage, [ContentPage])


class TestContentPage(WagtailPageTests):
    def test_can_create(self):
        """should be able to create contentpage under landingpage"""
        self.assertCanCreateAt(
            LandingPage,
            ContentPage,
            nested_form_data(
                {
                    "title": "Data Curation",
                    "slug": "data-curation",
                    "body": streamfield(
                        [
                            ("paragraph", rich_text("data curation page text")),
                        ]
                    ),
                }
            ),
        )

    def test_parent_pages(self):
        """allowed parents for contentpage should be home, landing, content"""
        self.assertAllowedParentPageTypes(
            ContentPage, [HomePage, LandingPage, ContentPage]
        )

    def test_subpages(self):
        """content page can only have other content pages as children"""
        self.assertAllowedSubpageTypes(ContentPage, [ContentPage])
