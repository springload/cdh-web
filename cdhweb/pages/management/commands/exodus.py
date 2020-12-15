"""Convert mezzanine-based pages to wagtail page models."""

import json

from django.core.management.base import BaseCommand, CommandError
from cdhweb.pages.models import HomePage, LandingPage, ContentPage
from cdhweb.resources.models import LandingPage as OldLandingPage
from mezzanine.pages.models import Page as MezzaninePage
from wagtail.core.blocks import RichTextBlock
from wagtail.core.models import Site, Page


class Command(BaseCommand):
    help = __file__.__doc__

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # TODO clear out all pages except root for idempotency
        # Page.objects.filter(depth__gt=1).delete()
        
        root = Page.objects.get(depth=1)

        # migrate the homepage
        ohp = MezzaninePage.objects.get(slug="/")
        homepage = HomePage(
            title=ohp.title,
            slug=ohp.slug,
            seo_title=ohp._meta_title or ohp.title,
            body=json.dumps([{
                "type": "paragraph",
                "value": ohp.richtextpage.content,
            }]),
            # Store description as search_description even if auto-generated
            search_description=ohp.description,
            first_published_at=ohp.created,
            last_published_at=ohp.updated,
        )
        root.add_child(instance=homepage)
        root.save()

        # migrate all landing pages
        for olp in OldLandingPage.objects.all():
            lp = LandingPage(
                title=olp.title,
                tagline=olp.tagline,
                slug=olp.slug,
                seo_title=olp._meta_title or olp.title,
                body=json.dumps([{
                    "type": "paragraph",
                    "value": olp.content,
                }]),
                search_description=olp.description,
                first_published_at=olp.created,
                last_published_at=olp.updated,
                # TODO not dealing with images yet
                # TODO not setting menu placement yet
                # TODO search keywords?
                # TODO set the correct visibility status
                # NOTE not login-restricting pages since we don't use it
                # NOTE not setting expiry date; handled manually
                # NOTE inclusion in sitemap being handled by sitemap itself
                # NOTE set has_unpublished_changes on page?
            )
            homepage.add_child(instance=lp)
        homepage.save()
