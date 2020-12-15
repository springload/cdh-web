"""Convert mezzanine-based pages to wagtail page models."""

import json

from django.core.management.base import BaseCommand, CommandError
from cdhweb.pages.models import HomePage, LandingPage, ContentPage
from cdhweb.resources.models import LandingPage as OldLandingPage
from mezzanine.pages.models import Page as MezzaninePage
from wagtail.core.blocks import RichTextBlock


class Command(BaseCommand):
    help = __file__.__doc__

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        homepage = HomePage.objects.get()

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
                # Only store description if it's not auto-generated
                search_description=olp.description,
                first_published_at=olp.created,
                last_published_at=olp.updated,
                # TODO not dealing with images yet
                # TODO not setting parent/child hierarchy yet
                # TODO not setting menu placement yet
                # TODO search keywords?
                # NOTE not login-restricting pages since we don't use it
            )
            # TODO create a revision that sets the body content of the page
            # TODO set the correct visibility status for the new revision
            # TODO set the correct publication date for the new revision
            # TODO set the created date for the new revision
            # TODO set the last updated date for the new revision
            # NOTE not setting expiry date; handled manually
            # NOTE inclusion in sitemap being handled by sitemap itself
            # NOTE set has_unpublished_changes on page?
            homepage.add_child(instance=lp)
        
        homepage.save()
