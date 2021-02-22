"""Exodus script for events."""
import logging

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.people.models import Person
from cdhweb.pages.exodus import convert_slug, get_wagtail_image, to_streamfield
from cdhweb.events.models import OldEvent, Event, EventsLinkPage


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
            search_description=event.description,
            image=get_wagtail_image(event.image),
            content=to_streamfield(event.content),
            thumbnail=get_wagtail_image(event.thumb),
        )

        # add it as child of event landing page so slugs are correct
        event_link.add_child(instance=event_page)
        event_link.save()

        # if the old event wasn't published, unpublish the new one
        if event.status != CONTENT_STATUS_PUBLISHED:
            event_page.unpublish()

        # add speakers
        for user in event.speakers.all():
            person = Person.objects.get(user=user)
            event_page.speakers.add(person)

        # NOTE no tags to migrate
        # TODO transfer attachments
