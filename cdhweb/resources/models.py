from django.db import models
from django.contrib.auth.models import User


class ResourceType(models.Model):
    '''Resource type for associating particular kinds of URLs
    with people and projects (e.g., project url, GitHub, Twitter, etc)'''
    resource_type = models.CharField(max_length=255)
    sort_order = models.IntegerField()
    # NOTE: defining the relationship here since we can't add to it to
    # django's auth.User directly
    users = models.ManyToManyField(User, through='UserResource',
        related_name='resources')

    def __str__(self):
        return self.resource_type


class UserResource(models.Model):
    '''Through-model for associating users with resource types and
    corresponding URLs for the specified resource type.'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    URL = models.URLField()

