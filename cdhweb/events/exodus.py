"""Exodus script for events."""
import logging

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.events.models import Event, EventsLinkPage, OldEvent, Speaker
from cdhweb.pages.exodus import (convert_slug, exodize_attachments,
                                 get_wagtail_image, to_streamfield)
from cdhweb.people.models import Person


def event_exodus():
    """Exodize all events models."""
    # get the top-level events link page
    try:
        event_link = EventsLinkPage.objects.get()
    except EventsLinkPage.DoesNotExist:
        return

    # create new event pages
    for event in OldEvent.objects.all():
        logging.debug("found mezzanine event %s" % event)

        # create event page
        event_page = Event(
            title=event.title,
            sponsor=event.sponsor,
            type=event.event_type,
            end_time=event.end_time,
            location=event.location,
            join_url=event.join_url,
            start_time=event.start_time,
            attendance=event.attendance,
            slug=convert_slug(event.slug),
            body=to_streamfield(event.content),
            search_description=event.description,
            image=get_wagtail_image(event.image),
            thumbnail=get_wagtail_image(event.thumb),
        )

        # add it as child of event landing page so slugs are correct
        event_link.add_child(instance=event_page)
        event_link.save()

        # if the old event wasn't published, unpublish the new one
        if event.status != CONTENT_STATUS_PUBLISHED:
            event_page.unpublish()

        # set publication dates
        event_page.first_published_at = event.publish_date
        event_page.last_published_at = event.updated
        event_page.save()

        # add speakers
        for user in event.speakers.all():
            person = Person.objects.get(user=user)
            Speaker.objects.create(person=person, event=event_page)

        # transfer attachments
        exodize_attachments(event, event_page)
        
        # NOTE no tags to migrate
