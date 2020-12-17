"""Convert mezzanine-based pages to wagtail page models."""

import json

from cdhweb.pages.models import ContentPage, HomePage, LandingPage
from cdhweb.resources.models import LandingPage as OldLandingPage
from django.core.management.base import BaseCommand
from django.db.models import Q
from mezzanine.pages import models as mezz_page_models
from wagtail.core.models import Page, Site


class Command(BaseCommand):
    help = __file__.__doc__

    # list to track migrated mezzanine pages by pk
    migrated = []

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
            tagline=page.landingpage.tagline,   # landing pages have a tagline
            slug=self.convert_slug(page.slug),
            seo_title=page._meta_title or page.title,
            body=json.dumps([{
                "type": "paragraph",
                "value": page.landingpage.content,
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

        # create a dummy top-level projects/ page for project pages to go under
        projects = ContentPage(
            title="Sponsored Projects",
            slug="projects",
            seo_title="Sponsored Projects",
        )
        homepage.add_child(instance=projects)
        homepage.save()
        self.migrated.append(mezz_page_models.Page.objects.get(slug='projects').pk)

        # create a dummy top-level events/ page for event pages to go under
        events = ContentPage(
            title="Events",
            slug="events",
            seo_title="Events"
        )
        homepage.add_child(instance=events)
        homepage.save()
        # mark events content page as migrated
        self.migrated.append(mezz_page_models.Page.objects.get(slug='events').pk)

        # migrate children of homepage
        for page in old_homepage.children.all():
            self.migrate_pages(page, homepage)

        # special cases
        # - migrate event pages but specify new events page as parent
        event_pages = mezz_page_models.Page.objects \
            .filter(Q(slug__startswith="events/") | Q(slug="year-of-data"))
        for page in event_pages:
            self.migrate_pages(page, events)
        # - migrate project pages but specify new projects list page as parent
        # - process about page last so project pages don't nest
        project_pages = mezz_page_models.Page.objects \
            .filter(slug__startswith="projects/").order_by('-slug')
        for page in project_pages:
            self.migrate_pages(page, projects)

        # migrate all remaining pages, starting with pages with no parent
        # (i.e., top level pages)
        for page in mezz_page_models.Page.objects.filter(parent__isnull=True):
            self.migrate_pages(page, homepage)

        # report on unmigrated pages
        unmigrated = mezz_page_models.Page.objects.exclude(pk__in=self.migrated)
        print('%d unmigrated mezzanine pages:' % unmigrated.count())
        for page in unmigrated:
            print('\t%s — slug/url %s)' % (page, page.slug))

    def migrate_pages(self, page, parent):
        """Recursively convert a mezzanine page and all its descendants
        to Wagtail pages with the same hierarchy.

        :params page: mezzanine page to convert
        :params parent: wagtail page the new page should be added to
        """

        # if a page has already been migrated, skip it
        if page.pk in self.migrated:
            return
        # create the new version of the page according to page type
        if hasattr(page, "richtextpage"):
            new_page = self.create_contentpage(page)
        elif hasattr(page, "landingpage"):
            new_page = self.create_landingpage(page)
        else:
            print('WARN: page conversion not yet handled for %s page' % (page))
            # bail out for now
            return

        parent.add_child(instance=new_page)
        parent.save()
        # add to list of migrated pages
        self.migrated.append(page.pk)

        # recursively create and add new versions of all this page's children
        for child in page.children.all():
            self.migrate_pages(child, new_page)
