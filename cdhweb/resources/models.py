from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from mezzanine.core.fields import FileField
from mezzanine.core.models import RichText
from mezzanine.pages.models import Page
from mezzanine.utils.models import upload_to


class ResourceType(models.Model):
    '''Resource type for associating particular kinds of URLs
    with people and projects (e.g., project url, GitHub, Twitter, etc)'''
    name = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
        null=False)
    # NOTE: defining the relationship here since we can't add to it to
    # django's auth.User directly
    users = models.ManyToManyField(User, through='UserResource',
        related_name='resources')

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.name


class UserResource(models.Model):
    '''Through-model for associating users with resource types and
    corresponding URLs for the specified resource type.'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()


class Attachment(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    file = FileField('Document', blank=True)
    url = models.URLField(blank=True)
    # TODO: needs validation (in admin?) to ensure one and only one of
    # file and url is set
    PDF = 'PDF'
    MSWORD = 'DOC'
    VIDEO = 'VIDEO'
    URL = 'URL'
    type_choices = (
        (PDF, 'PDF Document'),
        (MSWORD, 'MS Word Document'),
        (VIDEO, 'Video'),
        (URL, 'URL'),
    )
    attachment_type = models.CharField(max_length=255, choices=type_choices)
    # NOTE: possibly also validation on types? url/video for url,
    # pdf/word for file?

    # NOTE: could do a generic many-to-many with django-gm2m, but it seems
    # like it may be cleaner and simpler to just add many-to-many
    # relationships on the models where we want to allow attachments

    def __str__(self):
        return self.title


class LandingPage(Page, RichText):
    tagline = models.CharField(max_length=255)
    image = FileField(verbose_name="Image",
        upload_to=upload_to("resources.landing_pages.image", "resources"),
        format="Image", max_length=255, null=True, blank=True)

