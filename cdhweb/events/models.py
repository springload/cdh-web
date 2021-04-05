# -*- coding: utf-8 -*-

from datetime import datetime

import icalendar
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, MultiFieldPanel,
                                         StreamFieldPanel)
from wagtail.core.models import Page, PageManager, PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel

from cdhweb.pages.models import LinkPage, BasePage
from cdhweb.people.models import Person


class EventTypeManager(models.Manager):
    def get_by_natural_key(self, name):
        return self.get(name=name)


class EventType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    objects = EventTypeManager()

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name, )


class Location(models.Model):
    name = models.CharField(max_length=255,
                            help_text='Name of the location')
    short_name = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True,
                               help_text='Address of the location (will not display if same as name)')
    is_virtual = models.BooleanField(verbose_name="Virtual",
                                     default=False, help_text='Virtual platforms, i.e. Zoom or Google Hangouts')

    def __str__(self):
        return self.short_name or self.name

    class Meta:
        ordering = ("name",)

    @property
    def display_name(self):
        '''A name for template display'''
        if self.name and self.address and self.name != self.address:
            return ', '.join([self.name, self.address])
        return self.name

    def clean(self):
        # address is required for non-virtual events
        if not self.is_virtual and not self.address:
            raise ValidationError("Address is required for non-virtual events")


class EventQuerySet(PageQuerySet):

    def upcoming(self):
        '''Find upcoming events. Includes events that end on the current
        day even if the start time is past.'''
        now = timezone.now()
        # construct a datetime based on now but with zero hour/minute/second
        today = datetime(now.year, now.month, now.day,
                         tzinfo=timezone.get_default_timezone())
        return self.filter(end_time__gte=today)

    def recent(self):
        '''Find past events, most recent first.  Only includes events
        with end date in the past.'''
        now = timezone.now()
        # construct a datetime based on now but with zero hour/minute/second
        today = datetime(now.year, now.month, now.day,
                         tzinfo=timezone.get_default_timezone())
        return self.filter(end_time__lt=today).order_by('-start_time')


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
EventManager = PageManager.from_queryset(EventQuerySet)


class EventTag(TaggedItemBase):
    """Tags for Event pages."""
    content_object = ParentalKey(
        "events.Event", on_delete=models.CASCADE, related_name="tagged_items")


class Speaker(models.Model):
    """Relationship between Person and Event."""
    event = ParentalKey("events.Event", related_name="speakers")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    panels = [FieldPanel("person")]

    class Meta:
        # can't sort on related fields due to modelcluster limitations
        ordering = ("person",)

    def __str__(self) -> str:
        return "%s at %s" % (self.person, self.event)


class Event(BasePage, ClusterableModel):
    """Page type for an event, such as a workshop, lecture, or conference."""

    sponsor = models.CharField(max_length=80, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.ForeignKey(Location, null=True, blank=True,
                                 on_delete=models.SET_NULL)
    type = models.ForeignKey(EventType, null=True, on_delete=models.SET_NULL)
    attendance = models.PositiveIntegerField(null=True, blank=True,
                                             help_text="Total number of people who attended the event. (Internal only, for reporting purposes.)")
    join_url = models.URLField(verbose_name="Join URL", null=True, blank=True,
                               help_text="Join URL for virtual events, e.g. Zoom meetings.")
    image = models.ForeignKey("wagtailimages.image", null=True, blank=True,
                              on_delete=models.SET_NULL, related_name="+",
                              help_text="Image for display on event detail page (optional)")
    thumbnail = models.ForeignKey("wagtailimages.image", null=True, blank=True,
                                  on_delete=models.SET_NULL, related_name="+",
                                  help_text="Image for display on event card (optional)")
    people = models.ManyToManyField(Person, through=Speaker,
                                    related_name='events')
    tags = ClusterTaggableManager(through=EventTag, blank=True)
    # TODO attachments (#245)

    # can only be created underneath special link page
    parent_page_types = ["events.EventsLinkPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldPanel("type"),
        FieldRowPanel((FieldPanel("start_time"),
                       FieldPanel("end_time")), "Details"),
        FieldPanel("location"),
        FieldPanel("join_url"),
        FieldRowPanel((FieldPanel("sponsor"),
                       FieldPanel("attendance")), "Tracking"),
        FieldRowPanel((ImageChooserPanel("thumbnail"),
                       ImageChooserPanel("image")), "Images"),
        MultiFieldPanel(
            (InlinePanel("speakers", label="Speaker"),), heading="Speakers"),
        StreamFieldPanel("body"),
        StreamFieldPanel("attachments")
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("tags")
    ]

    # custom manager/queryset logic
    objects = EventManager()

    class Meta:
        ordering = ("-start_time",)

    def __str__(self):
        return " - ".join([self.title, self.start_time.strftime("%b %d, %Y")])

    @property
    def speaker_list(self):
        """Comma-separated list of speaker names."""
        return ", ".join(str(speaker.person) for speaker in self.speakers.all())

    def clean(self):
        """Validate that a type was specified for this event."""
        # NOTE we can't cascade deletes to wagtail pages without corrupting the
        # page tree. Instead, we use SET_NULL and a clean() handler so that we
        # can make sure that it's impossible to create an Event without a type.
        # More info: https://github.com/wagtail/wagtail/issues/1602
        if not self.type:
            raise ValidationError("Event must specify a type.")

    def get_url_parts(self, *args, **kwargs):
        """Custom event page URLs of the form /events/2014/03/my-event."""
        url_parts = super().get_url_parts(*args, **kwargs)
        # NOTE evidently this can sometimes be None; unclear why – perhaps it
        # gets called in a context where the request is unavailable? Only
        # happens in QA, not locally.
        if url_parts:
            site_id, root_url, _ = url_parts
            page_path = reverse("events:detail", kwargs={
                "year": self.start_time.year,
                # force two-digit month
                "month": "%02d" % self.start_time.month,
                "slug": self.slug,
            })
            return site_id, root_url, page_path

    def get_ical_url(self):
        """URL to download this event as a .ics (iCal) file."""
        return reverse('events:ical', kwargs={
            'year': self.start_time.year,
            # force two-digit month
            'month': '%02d' % self.start_time.month,
            'slug': self.slug})

    def is_virtual(self):
        """If an event takes place in a virtual location, it is virtual"""
        if self.location:
            return self.location.is_virtual
        return False
    is_virtual.boolean = True
    is_virtual.short_description = "Virtual"

    def when(self):
        """Event start/end date and time, formatted for display.

        Removes leading zeros from hours and converts am/pm to lower case.
        """

        # NOTE: - in %-I is to remove leading zero
        # (possibly platform specific?)

        local_tz = timezone.get_default_timezone()
        # convert dates to local timezone for display
        local_start = self.start_time.astimezone(local_tz)
        local_end = self.end_time.astimezone(local_tz)
        start = " ".join([local_start.strftime("%b %d"),
                          local_start.strftime("%-I:%M")])
        start_ampm = local_start.strftime("%p")
        # include start am/pm if *different* from end
        if start_ampm != local_end.strftime("%p"):
            start += " %s" % start_ampm.lower()

        # include end month and day if *different* from start
        end_pieces = []
        if local_start.month != local_end.month:
            end_pieces.append(local_end.strftime("%b %d"))
        elif local_start.day != local_end.day:
            end_pieces.append(local_end.strftime("%d"))
        end_pieces.append(local_end.strftime("%-I:%M %p").lower())
        end = " ".join(end_pieces)

        return " – ".join([start, end])

    def duration(self):
        """duration between start and end time as :class:`datetime.timedelta`"""
        return self.end_time - self.start_time

    def ical_event(self):
        """Return the current event as a :class:`icalendar.Event` for
        inclusion in a :class:`icalendar.Calendar`"""
        event = icalendar.Event()
        # use absolute url for event id and in event content
        absurl = self.get_full_url()
        event.add("uid", absurl)
        event.add("summary", self.title)
        event.add("dtstart", self.start_time)
        event.add("dtend", self.end_time)
        if self.location:
            if self.is_virtual() and self.join_url:
                event.add("location", self.join_url)
            else:
                event.add("location", self.location.display_name)
        event.add("description",
                  "\n".join([strip_tags(self.body), "", absurl]))
        return event


class EventsLinkPage(LinkPage):
    """Container page that defines where Project pages can be created."""
    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is an Event; this is so that
    # Events made in the admin automatically are created here.
    subpage_types = [Event]
