"""Exodus utilities for pages"""

import json
import logging
import os

from bs4 import BeautifulSoup
from django.utils.html import strip_tags
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.images.models import Image
from wagtail.core.blocks.stream_block import StreamValue
from wagtail.snippets.blocks import SnippetChooserBlock

from cdhweb.pages.models import (ContentPage, HomePage, LandingPage, LinkPage,
                                 PageIntro, ExternalAttachment, LocalAttachment)


def is_blank(content):
    """check for if mezzanine page content is whitespace only"""
    # remove non-breaking space, strip tags, strip whitespace
    return not strip_tags(content.replace('&nbsp;', '')).strip()


def convert_slug(slug):
    """Convert a Mezzanine slug into a Wagtail slug."""
    # wagtail stores only the final portion of a URL with no slashes
    # remove trailing slash, then return final portion without slashes
    return slug.rstrip("/").split("/")[-1]


def to_streamfield(content):
    """Output a json object for given richtext as a "migrated" streamfield."""
    # Wagtail chokes on unclosed <img> tags, throwing: "Unmatched tags:
    # expected img, got figure". There may be other issues lurking in the html
    # from mezzanine. Instead of trying to parse it with a regex, we let a real
    # parser (BeautifulSoup) do the work.
    pretty_content = BeautifulSoup(content, "lxml").prettify()
    return json.dumps([{"type": "migrated", "value": pretty_content}])


def to_streamfield_safe(content):
    """Same as to_streamfield, but does no HTML validation and creates a block
    of type 'paragraph' instead of migrated. Used for testing."""
    return json.dumps([{"type": "paragraph", "value": content}])


def get_wagtail_image(image):
    """get the migrated wagtail image for a foreign-key image using image file 
    basename, which is migrated as image title"""
    if not image:
        return None
    try:
        return Image.objects.get(title=os.path.basename(image.name))
    except Image.DoesNotExist as err:
        logging.warning("%s: %s" % (image, err))
        return None


def exodize_attachments(mezzanine_page, wagtail_page):
    """Convert all mezzanine page attachments and attach to the wagtail page."""
    if mezzanine_page.old_attachments.exists():
        # convert all attachment to new models
        new_attachments = []
        for attachment in mezzanine_page.old_attachments.all():
            # if it has a URL, create an ExternalAttachment or use existing
            if attachment.url:
                logging.debug("exodizing link attachment %s" % attachment)
                new_attachments.append(ExternalAttachment.objects.get_or_create(
                    url=attachment.url,
                    title=attachment.title,
                    author=attachment.author,
                )[0])
            # otherwise create a LocalAttachment (Document) or use existing
            else:
                logging.debug("exodizing uploaded attachment %s" % attachment)
                new_attachments.append(LocalAttachment.objects.get_or_create(
                    file=attachment.file,
                    title=attachment.title,
                    author=attachment.author,
                )[0])
        # associate new attachments with new wagtail page
        attachments_field = [("link" if attachment.url else "document", attachment)
                             for attachment in new_attachments]
        logging.debug("attachments for %s: %s" %
                      (wagtail_page, attachments_field))
        wagtail_page.attachments = attachments_field
    return wagtail_page


def create_homepage(page):
    """Create and return a Wagtail homepage based on a Mezzanine page."""
    return HomePage(
        title=page.title,
        slug=convert_slug(page.slug),
        seo_title=page._meta_title or page.title,
        body=to_streamfield(page.richtextpage.content),
        search_description=page.description,    # store even if generated
    )


def create_landingpage(page):
    """Create and return a Wagtail landing page based on a Mezzanine page."""
    return LandingPage(
        title=page.title,
        tagline=page.landingpage.tagline,   # landing pages have a tagline
        header_image=get_wagtail_image(page.landingpage.image),
        slug=convert_slug(page.slug),
        seo_title=page._meta_title or page.title,
        body=to_streamfield(page.landingpage.content),
        search_description=page.description,    # store even if generated
        # TODO not setting menu placement yet
        # NOTE not migrating search keywords
    )


def create_contentpage(page):
    """Create and return a Wagtail content page based on a Mezzanine page."""
    return ContentPage(
        title=page.title,
        slug=convert_slug(page.slug),
        seo_title=page._meta_title or page.title,
        # access via richtextpage when present
        body=to_streamfield(page.richtextpage.content) if hasattr(
            page, "richtextpage") else to_streamfield(""),
        search_description=page.description,    # store even if generated
        # TODO not setting menu placement yet
        # NOTE not migrating search keywords
        # NOTE not login-restricting pages since we don't use it
        # NOTE not setting expiry date; handled manually
        # NOTE inclusion in sitemap being handled by sitemap itself
        # NOTE publication status must be handled after creation
    )


def create_link_page(page, parent):
    '''generate link pages for content served by django views'''
    # link page is needed for menus; should use existing title and full slug
    new_page = LinkPage(
        title=page.title,
        link_url=page.slug,
        slug=convert_slug(page.slug)
    )
    parent.add_child(instance=new_page)

    # if the page is not blank, create a page intro snippet with the content
    if page.richtextpage.content and \
            not is_blank(page.richtextpage.content):
        PageIntro.objects.create(page=new_page,
                                 paragraph=page.richtextpage.content)


def form_pages():
    """migrate embedded google forms from mezzanine templates"""
    # add new migrated to body with iframe from engage/consult template and save
    # set a height on the iframe to ensure it renders correctly
    if ContentPage.objects.filter(slug="consult").exists():
        consults = ContentPage.objects.get(slug="consult")
        consults.body = json.dumps([
            {"type": "migrated", "value": consults.body[0].value.source},
            {"type": "migrated", "value": '<iframe title="Consultation Request Form" height="2400" src="https://docs.google.com/forms/d/e/1FAIpQLScerpyeQAgp91Iy66c1rKbKSwbSpeuB5yHh14l3G9C86eUjsA/viewform?embedded=true">Loading...</iframe>'}
        ])
        consults.save()
    # # do the same for cosponsorship page
    if ContentPage.objects.filter(slug="cosponsor").exists():
        cosponsor = ContentPage.objects.get(slug="cosponsor")
        cosponsor.body = json.dumps([
            {"type": "migrated", "value": cosponsor.body[0].value.source},
            {"type": "migrated", "value": '<iframe title="Cosponsorship Request Form" height="3250" src="https://docs.google.com/forms/d/e/1FAIpQLSeP40DBM7n8GYgW_i99nRxY5T5P39DrIWyIwq9LggIwu4r5jQ/viewform?embedded=true">Loading...</iframe>'}
        ])
        cosponsor.save()
