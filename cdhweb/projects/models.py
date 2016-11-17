from django.contrib.auth.models import User
from django.db import models
from mezzanine.core.fields import RichTextField, FileField
from mezzanine.core.models import Displayable

from cdhweb.resources.models import ResourceType


class Project(Displayable):
    name = models.CharField(max_length=255)
    # project_subtitle = models.CharField(max_length=80, blank=True, null=True)
    short_description = models.CharField(max_length=255)
    long_description = RichTextField()
    is_active = models.BooleanField()

    members = models.ManyToManyField(User, through='Membership')
    resources = models.ManyToManyField(ResourceType, through='ProjectResource')

    def __str__(self):
        return self.name

    # TODO: default sorting?


class GrantType(models.Model):
    grant_type = models.CharField(max_length=255)

    def __str__(self):
        return self.grant_type


class Grant(models.Model):
    project = models.ForeignKey(Project)
    grant_type = models.ForeignKey(GrantType)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return '%s %s (%s)' % (self.project.name, self.grant_type.grant_type,
            self.start_date.year)


# fixme: where does resource type go, for associated links?

class Role(models.Model):
    title = models.CharField(max_length=255)
    sort_order = models.IntegerField()

    def __str__(self):
        return self.title


class Membership(models.Model):
    project = models.ForeignKey(Project)
    user = models.ForeignKey(User)
    grant = models.ForeignKey(Grant)
    role = models.ForeignKey(Role)

    def __str__(self):
        return '%s - %s on %s' % (self.user, self.role, self.grant)


class ProjectResource(models.Model):
    '''Through-model for associating projects with resource types and
    URLs'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    URL = models.URLField()