"""Convert mezzanine-based pages to wagtail page models."""

import json
from collections import defaultdict

from cdhweb.pages.models import ContentPage, HomePage, LandingPage
from cdhweb.resources.models import LandingPage as OldLandingPage
from django.core.management.base import BaseCommand
from mezzanine.pages import models as mezz_page_models
from wagtail.core.models import Page, Site


class Command(BaseCommand):
    help = __file__.__doc__

    def convert_slug(self, slug):
        """Convert a Mezzanine slug into a Wagtail slug."""
        # wagtail stores only the final portion of a URL with no slashes
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
                "value": page.richtextpage.content,   # access via richtextpage
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

    def handle(self, *args, **options):
        """Create Wagtail pages for all extant Mezzanine pages."""
        # clear out wagtail pages for idempotency
        Page.objects.filter(depth__gt=2).delete()

        # create the new homepage
        old_homepage = mezz_page_models.Page.objects.get(slug="/")
        homepage = self.create_homepage(old_homepage)
        root = Page.objects.get(depth=1)
        root.add_child(instance=homepage)
        root.save()

        # point the default site at the new homepage and delete old homepage(s).
        # if they are deleted prior to switching site.root_page, the site will
        # also be deleted in a cascade, which we don't want
        site = Site.objects.get()
        site.root_page = homepage
        site.save()
        Page.objects.filter(depth=2).exclude(pk=homepage.pk).delete()

        # track content pages to migrate and their parents
        queue = []
        parent = defaultdict(Page)
        parent[old_homepage] = root

        # add all top-level content pages and landing pages to the queue
        for page in list(old_homepage.children.all()) + \
                    list(OldLandingPage.objects.all()):
            queue.append(page)
            parent[page] = homepage

        # perform breadth-first search of all content pages
        while queue:
            # figure out what page type to create, and create it
            page = queue.pop(0)
            if hasattr(page, "richtextpage"):
                new_page = self.create_contentpage(page)
            else:
                new_page = self.create_landingpage(page)
            try:
                parent[page].add_child(instance=new_page)
                parent[page].save()
                # add all the pages at the next level down to the queue
                for child in page.children.all():
                    queue.append(child)
                    parent[child] = new_page
            # FIXME slugs
            except:
                pass

