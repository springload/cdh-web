"""Convert mezzanine-based pages to wagtail page models."""

import json

from cdhweb.pages.models import ContentPage, HomePage, LandingPage
from cdhweb.resources.models import LandingPage as OldLandingPage
from django.core.management.base import BaseCommand
from mezzanine.pages import models as mezz_page_models
from wagtail.core.models import Page, Site


class Command(BaseCommand):
    help = __file__.__doc__

    def convert_slug(self, slug):
        """Convert a Mezzanine slug into a Wagtail slug."""
        # wagtail stores only the final portion of a URL: ""
        # remove trailing slash, then return final portion without slashes
        return slug.rstrip("/").split("/")[-1]

    def create_homepage(self, page):
        """Create and return a Wagtail homepage based on a Mezzanine page."""
        return HomePage(
            title=page.title,
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "paragraph",
                "value": page.richtextpage.content,   # access via richtextpage
            }]),
            search_description=page.description,    # store even if generated
            first_published_at=page.created,
            last_published_at=page.updated,
        )

    def create_landingpage(self, page):
        """Create and return a Wagtail landing page based on a Mezzanine page."""
        return LandingPage(
            title=page.title,
            tagline=page.tagline,   # landing pages have a tagline
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "paragraph",
                "value": page.content,
            }]),
            search_description=page.description,    # store even if generated
            first_published_at=page.created,
            last_published_at=page.updated,
            # TODO not dealing with images yet
            # TODO not setting menu placement yet
            # TODO search keywords?
        )

    def create_contentpage(self, page):
        """Create and return a Wagtail content page based on a Mezzanine page."""
        return ContentPage(
            title=page.title,
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "paragraph",
                "value": page.richtextpage.content,
            }]),
            search_description=page.description,    # store even if generated
            first_published_at=page.created,
            last_published_at=page.updated,
            # TODO not dealing with images yet
            # TODO not setting menu placement yet
            # TODO search keywords?
            # TODO set the correct visibility status
            # NOTE not login-restricting pages since we don't use it
            # NOTE not setting expiry date; handled manually
            # NOTE inclusion in sitemap being handled by sitemap itself
            # NOTE set has_unpublished_changes on page?
        )

    def walk(self, page, depth):
        """Recursively create Wagtail content pages."""
        # create the new version of the page
        new_page = self.create_contentpage(page)
        new_page.depth = depth
        # recursively create the new versions of all the page's children
        for child in page.children.all():
            new_page.add_child(instance=self.walk(child, depth + 1))
        # return the new page
        return new_page

    def handle(self, *args, **options):
        """Convert all existing Mezzanine pages to Wagtail pages."""
        # clear out all pages except root and homepage for idempotency
        site = Site.objects.get()
        old_root_page = site.root_page
        Page.objects.filter(depth__gt=2).delete()
        root = Page.objects.get(depth=1)

        # migrate the homepage
        old_homepage = mezz_page_models.Page.objects.get(slug="/")
        homepage = self.create_homepage(old_homepage)
        root.add_child(instance=homepage)
        root.save()

        # point site at the new root page before deleting the old one to avoid
        # deleting the site in a cascade
        site.root_page = homepage
        site.save()
        old_root_page.delete()

        # migrate all landing pages
        for old_landingpage in OldLandingPage.objects.all():
            landingpage = self.create_landingpage(old_landingpage)
            homepage.add_child(instance=landingpage)
        homepage.save()

        # migrate all content pages
        # direct children of homepage
        for child in old_homepage.children.all():
            if child.richtextpage:
                self.walk(child, 3)
        # children of landingpage
        for old_landingpage in OldLandingPage.objects.all():
            for child in old_landingpage.children.all():
                self.walk(child, 4)
        homepage.save()
