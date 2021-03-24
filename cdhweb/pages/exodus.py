"""Exodus utilities for pages"""

import json
import logging
import os
from json.decoder import JSONDecodeError

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.admin.models import ADDITION, CHANGE, DELETION, LogEntry
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.html import strip_tags
from wagtail.core.models import PageLogEntry
from wagtail.images.models import Image

from cdhweb.pages.models import (ContentPage, ExternalAttachment, HomePage,
                                 LandingPage, LinkPage, LocalAttachment,
                                 PageIntro)

LOG_ENTRY_ACTIONS = {
    CHANGE: "wagtail.edit",
    ADDITION: "wagtail.create",
    DELETION: "wagtail.delete"
}


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
    # derived Displayables like Project have attachments defined directly as a
    # m2m; other pages may not and so we need to use the reverse relationship
    attachments = getattr(mezzanine_page, "attachments", None) or \
        mezzanine_page.old_attachments
    if attachments.exists():
        # convert all attachment to new models
        new_attachments = []
        for attachment in attachments.all():
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
        attachments_field = [("link" if isinstance(attachment, ExternalAttachment) else "document", attachment)
                             for attachment in new_attachments]
        logging.debug("attachments for %s: %s" %
                      (wagtail_page, attachments_field))
        wagtail_page.attachments = attachments_field
        wagtail_page.save(log_action=False)
    return wagtail_page


def exodize_history(mezzanine_page, wagtail_page):
    """Create log entries for new wagtail page corresponding to old page.

    Also adds a log entry noting that the page was exodized.
    """
    # make sure the page has only one real creation event; we want to use
    # the date it was created in mezzanine
    creation = PageLogEntry.objects.get(page=wagtail_page,
                                        action="wagtail.create")
    creation.delete()

    # get all the old admin log entries for this page. content pages will
    # have entries associated with their most specific subclass, but other
    # page models won't, so we just use get_for_model directly. save the 
    # user and timestamp from the most recent edit for later.
    try:
        specific_model = getattr(mezzanine_page, mezzanine_page.content_model)
    except AttributeError:
        specific_model = mezzanine_page
    ctype = ContentType.objects.get_for_model(specific_model)
    entries = LogEntry.objects.filter(object_id=mezzanine_page.pk,
                                      content_type_id=ctype.pk)
    User = get_user_model()
    if entries.exists():
        logging.debug("exodizing %d log entries for %s" %
                      (entries.count(), mezzanine_page))
        last_user = User.objects.get(pk=entries.first().user_id)
        last_edit = entries.first().action_time
    else:
        last_user = None
        last_edit = timezone.now()

    # create log entries for new wagtail page to match old page.
    # if there's any data about the change, we can store it as a JSON
    # string with the entry. it's not visible in admin, but it can be
    # used later. this is sometimes populated and sometimes not
    for entry in entries:
        try:
            data = json.loads(entry.get_change_message())
        except JSONDecodeError:
            data = None
        PageLogEntry.objects.log_action(
            instance=wagtail_page,
            data=data,
            action=LOG_ENTRY_ACTIONS[entry.action_flag],
            timestamp=entry.action_time,
            title=entry.object_repr,
            user=User.objects.get(pk=entry.user_id)
        )

    # create an initial wagtail revision pointing to the most recent page data.
    # without this, the "history" button won't display in the admin until you
    # create a new draft or publish for the first time.
    script_user = User.objects.get(username=settings.SCRIPT_USERNAME)
    revision = wagtail_page.save_revision(
        user=last_user or script_user,
        changed=False,
        log_action=False
    )
    revision.created_at = last_edit
    revision.save()
    wagtail_page.latest_revision_created_at = last_edit
    wagtail_page.save(log_action=False)


    # add a custom entry logging the actual exodus. see `wagtail_hooks.py`
    # for the definition of the custom "exodus" action.
    PageLogEntry.objects.log_action(
        instance=wagtail_page,
        data={
            "old_pk": mezzanine_page.pk,
            "old_slug": mezzanine_page.slug,
            "old_title": mezzanine_page.title
        },
        action="cdhweb.exodus",
        user=script_user
    )
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


def create_landingpage(page, page_type=LandingPage):
    """Create and return a Wagtail landing page based on a Mezzanine page."""
    return page_type(
        title=page.title,
        tagline=page.landingpage.tagline,   # landing pages have a tagline
        header_image=get_wagtail_image(page.landingpage.image),
        slug=convert_slug(page.slug),
        seo_title=page._meta_title or page.title,
        body=to_streamfield(page.landingpage.content),
        search_description=page.description,    # store even if generated
        # map mezzanine main nav/footer to wagtail in menu
        show_in_menus=any(val in page.in_menus
                          for val in ['1', '3'])
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
        # map mezzanine main nav/footer to wagtail in menu
        show_in_menus=any(val in page.in_menus
                          for val in ['1', '3'])
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
        slug=convert_slug(page.slug),

    )
    parent.add_child(instance=new_page)

    # if the page is not blank, create a page intro snippet with the content
    if page.richtextpage.content and \
            not is_blank(page.richtextpage.content):
        PageIntro.objects.create(page=new_page,
                                 paragraph=page.richtextpage.content)

    return new_page


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
        consults.save(log_action=False)
    # # do the same for cosponsorship page
    if ContentPage.objects.filter(slug="cosponsor").exists():
        cosponsor = ContentPage.objects.get(slug="cosponsor")
        cosponsor.body = json.dumps([
            {"type": "migrated", "value": cosponsor.body[0].value.source},
            {"type": "migrated", "value": '<iframe title="Cosponsorship Request Form" height="3250" src="https://docs.google.com/forms/d/e/1FAIpQLSeP40DBM7n8GYgW_i99nRxY5T5P39DrIWyIwq9LggIwu4r5jQ/viewform?embedded=true">Loading...</iframe>'}
        ])
        cosponsor.save(log_action=False)
