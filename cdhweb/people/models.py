from django.db import models
from django.contrib.auth.models import User
from mezzanine.core.fields import RichTextField, FileField
from mezzanine.core.managers import DisplayableManager
from mezzanine.core.models import Displayable


class Title(models.Model):
    '''Job titles for people'''
    title = models.CharField(max_length=255)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
        null=False)
    # NOTE: defining relationship here because we can't add it to User
    # directly
    positions = models.ManyToManyField(User, through='Position',
        related_name='positions')

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title

    def num_people(self):
        '''Number of people with this position title'''
        # NOTE: maybe more meaningful if count restrict to _current_ titles?
        return self.positions.distinct().count()
    num_people.short_description = '# People'


class Person(User):
    # NOTE: using a proxy model for User so we can customize the
    # admin interface in one place without having to extend the django
    # default user model.
    class Meta:
        proxy = True
        verbose_name_plural = 'People'

    @property
    def current_title(self):
        return self.positions.first()


class Profile(Displayable):
    user = models.OneToOneField(User)
    education = RichTextField()
    bio = RichTextField()
    # NOTE: could use regex here, but how standard are staff phone
    # numbers? or django-phonenumber-field, but that's probably overkill
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    office_location = models.CharField(max_length=255, blank=True, null=True)

    # use displayable manager for access to published queryset filter, etc.
    objects = DisplayableManager()

    def __str__(self):
        return ' '.join(self.user.first_name, self.user.last_name)


class Position(models.Model):
    '''Through model for many-to-many relation between people
    and titles.  Adds start and end dates to the join table.'''
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return '%s %s (%s)' % (self.user, self.title, self.start_date.year)


# FIXME: where does this really belong? Used for both users and projects,
# but not really specific to either; but seems overkill to make a separate app
class ResourceType(models.Model):
    '''Resource type for associating particular kinds of URLs
    with people and projects (e.g., project url, GitHub, Twitter, etc)'''
    resource_type = models.CharField(max_length=255)
    sort_order = models.IntegerField()
    # NOTE: defining the relationship here since we can't add to User directly
    users = models.ManyToManyField(User, through='UserResource',
        related_name='resources')


class UserResource(models.Model):
    '''Through-model for associating users with resource types and
    corresponding URLs for the specified resource type.'''
    resource_type = models.ForeignKey(ResourceType, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    URL = models.URLField()