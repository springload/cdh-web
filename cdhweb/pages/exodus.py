"""Exodus utilities for pages"""

import json
import logging
import os

from django.utils.html import strip_tags
from wagtail.images.models import Image

from cdhweb.pages.models import (ContentPage, HomePage, LandingPage, LinkPage,
                                 PageIntro)


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
    return json.dumps([{"type": "migrated", "value": content}])


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
        link_url=page.slug)
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
