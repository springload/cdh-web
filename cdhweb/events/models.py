from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone

from mezzanine.core.fields import FileField
from mezzanine.core.models import Displayable, RichText
from mezzanine.core.managers import DisplayableManager
from mezzanine.utils.models import AdminThumbMixin, upload_to
from taggit.managers import TaggableManager


class EventType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=255)
    short_name = models.CharField(max_length=80, blank=True)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.short_name or self.name


class EventQuerySet(models.QuerySet):

    def upcoming(self):
        return self.filter(start_time__gt=timezone.now())


class EventManager(DisplayableManager):
    # extend displayable manager to preserve access to published filter
    def get_queryset(self):
        return EventQuerySet(self.model, using=self._db)

    def upcoming(self):
        return self.get_queryset().upcoming()


class Event(Displayable, RichText, AdminThumbMixin):
    # description = rich text field
    # NOTE: do we want a sponsor field? or jest include in description?
    sponsor = models.CharField(max_length=80, null=True, blank=True)
    image = FileField(verbose_name='Image',
        upload_to=upload_to("events.Event.image", "event"),
        format="Image", max_length=255, null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.ForeignKey(Location)
    event_type = models.ForeignKey(EventType)
    speakers = models.ManyToManyField(User,
        help_text='Guest lecturer(s) or Workshop leader(s)')

    tags = TaggableManager()

    # override default manager with custom version
    objects = EventManager()

    admin_thumb_field = "image"
    event_type.verbose_name = 'Type'

    def __str__(self):
        return '%s - %s' % (self.title, self.start_time.strftime('%b %d, %Y'))

    class Meta:
        ordering = ("start_time",)

    def get_absolute_url(self):
        # we don't have to worry about the various url config options
        # that mezzanine has to support; just handle the url style we
        # want to use locally
        return reverse('event:detail', kwargs={
            'year': self.publish_date.year,
            'month': self.publish_date.month,
            'slug': self.slug})