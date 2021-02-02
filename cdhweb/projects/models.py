from cdhweb.pages.models import BodyContentBlock, LandingPage, RelatedLink
from cdhweb.people.models import Person
from cdhweb.resources.models import Attachment, DateRange, ExcerptMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from mezzanine.core.fields import FileField, RichTextField
from mezzanine.core.models import Displayable
from mezzanine.utils.models import AdminThumbMixin, upload_to
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.managers import TaggableManager
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (FieldPanel, FieldRowPanel,
                                         InlinePanel, StreamFieldPanel)
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, PageManager, PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel


class ProjectQuerySet(PageQuerySet):

    def highlighted(self):
        '''return projects that are marked as highlighted'''
        return self.filter(highlight=True)

    def _current_grant_query(self):
        '''QuerySet filter to find projects with a current grant,
        based on start date before current date and end date after current
        date or not set.
        '''
        today = timezone.now()
        return (models.Q(grants__start_date__lt=today) &
                (models.Q(grants__end_date__gt=today) |
                 models.Q(grants__end_date__isnull=True)))

    def current(self):
        '''Projects with a current grant, based on dates'''
        return self.filter(self._current_grant_query()).distinct()

    def not_current(self):
        '''Projects with no current grant, based on dates'''
        return self.exclude(self._current_grant_query())

    #: grant types that indicate staff or postdoc project
    staff_postdoc_grants = ['Staff R&D',
                            'Staff Project', 'Postdoctoral Research Project']

    def staff_or_postdoc(self):
        '''Staff and postdoc projects, based on grant type'''
        return self.filter(grants__grant_type__grant_type__in=self.staff_postdoc_grants) \
            .exclude(working_group=True)

    def not_staff_or_postdoc(self):
        '''Exclude staff and postdoc projects, based on grant type'''
        return self.exclude(grants__grant_type__grant_type__in=self.staff_postdoc_grants) \
            .exclude(working_group=True)

    def working_groups(self):
        '''Include only projects with the working group flag set'''
        return self.filter(working_group=True)

    def order_by_newest_grant(self):
        '''order by grant start date, most recent grants first; secondary
        sort by project title'''
        # NOTE: using annotation to get just the most recent start date
        # to avoid issues with projects appearing multiple times.
        return self.annotate(last_start=models.Max('grants__start_date')) \
                   .order_by('-last_start', 'title')


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
ProjectManager = PageManager.from_queryset(ProjectQuerySet)


class OldProject(Displayable, AdminThumbMixin, ExcerptMixin):
    '''A CDH sponsored project'''

    short_description = models.CharField(max_length=255, blank=True,
                                         help_text='Brief tagline for display on project card in browse view')
    long_description = RichTextField()
    highlight = models.BooleanField(default=False,
                                    help_text='Include in randomized project display on the home page.')
    cdh_built = models.BooleanField('CDH Built', default=False,
                                    help_text='Project built by CDH Development & Design team.')
    working_group = models.BooleanField(
        'Working Group', default=False, help_text='Project is a long-term collaborative group associated with the CDH.')

    tags = TaggableManager(blank=True)

    # TODO: include help text to indicate images are optional, where they
    # are used (size?); add language about putting large images in the
    # body of the project description, when we have styles for that.
    image = FileField(verbose_name="Image",
                      upload_to=upload_to("projects.image", "projects"),
                      format="Image", max_length=255, null=True, blank=True)

    thumb = FileField(verbose_name="Thumbnail",
                      upload_to=upload_to(
                          "projects.image", "projects/thumbnails"),
                      format="Image", max_length=255, null=True, blank=True)

    attachments = models.ManyToManyField(Attachment, blank=True)

    # custom manager and queryset
    objects = ProjectQuerySet.as_manager()

    admin_thumb_field = "thumb"

    # TODO: Insert panels after creating project wagtail page
    # content_panels = Page.content_panels + [
    #     #....
    #     InlinePanel("related_links", heading="Related Links"),
    # ]

    class Meta:
        # sort by project title for now
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project:detail', kwargs={'slug': self.slug})

    @property
    def website_url(self):
        '''website url, if set'''
        website = self.related_links \
            .filter(type__name='Website').first()
        if website:
            return website.url

    def latest_grant(self):
        '''Most recent :class:`Grant`'''
        if self.grant_set.count():
            return self.grant_set.order_by('-start_date').first()

    def current_memberships(self):
        ''':class:`MembershipQueryset` of current members sorted by role'''
        # uses memberships rather than members so that we can retain role
        # information attached to the membership
        today = timezone.now().date()
        # if the last grant for this project is over, display the team
        # for that grant period
        latest_grant = self.latest_grant()
        if latest_grant and latest_grant.end_date and \
           latest_grant.end_date < today:
            return self.membership_set \
                .filter(start_date__lte=latest_grant.end_date) \
                .filter(
                    models.Q(end_date__gte=latest_grant.start_date) |
                    models.Q(end_date__isnull=True)
                )

        # otherwise, return current members based on date
        return self.membership_set.filter(start_date__lte=today) \
            .filter(
                models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)
        )

    def alums(self):
        ''':class:`PersonQueryset` of past members sorted by last name'''
        # uses people rather than memberships so that we can use distinct()
        # to ensure people aren't counted multiple times for each grant
        # and because we don't care about role (always 'alum')
        return self.members \
            .distinct() \
            .exclude(membership__in=self.current_memberships()) \
            .order_by('last_name')


class ProjectTag(TaggedItemBase):
    """Tags for Project pages."""
    content_object = ParentalKey(
        "projects.Project", on_delete=models.CASCADE, related_name="tagged_items")


class Project(Page, ClusterableModel):
    """Page type for a CDH sponsored project or working group."""
    short_description = models.CharField(max_length=255, blank=True,
                                         help_text="Brief tagline for display on project card in browse view")
    long_description = StreamField(BodyContentBlock, blank=True)
    highlight = models.BooleanField(default=False,
                                    help_text="Include in randomized project display on the home page.")
    cdh_built = models.BooleanField("CDH Built", default=False,
                                    help_text="Project built by CDH Development & Design team.")
    working_group = models.BooleanField(
        "Working Group", default=False, help_text="Project is a long-term collaborative group associated with the CDH.")
    image = models.ForeignKey('wagtailimages.image', null=True,
                              blank=True, on_delete=models.SET_NULL,
                              related_name='+')
    thumbnail = models.ForeignKey('wagtailimages.image', null=True,
                                  blank=True, on_delete=models.SET_NULL,
                                  related_name='+')
    members = models.ManyToManyField(Person, through="Membership")
    tags = ClusterTaggableManager(through=ProjectTag, blank=True)
    updated = models.DateTimeField(auto_now=True, null=True, editable=False)

    # can only be created underneath landing page
    parent_page_types = ["projects.ProjectsLandingPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldRowPanel((FieldPanel("highlight"),
                       FieldPanel("cdh_built"),
                       FieldPanel("working_group")), "Settings"),
        FieldRowPanel((ImageChooserPanel("thumbnail"),
                        ImageChooserPanel("image")), "Images"),
        FieldPanel("short_description"),
        StreamFieldPanel("long_description"),
        InlinePanel("grants", label="Grants"),
        InlinePanel("memberships", label="Members"),
        # TODO add inline editing for ProjectRelatedLink (#181)
    ]
    promote_panels = Page.promote_panels + [
        FieldPanel("tags")
    ]

    # custom manager/queryset logic
    objects = ProjectManager()

    def __str__(self):
        return self.title

    @property
    def website_url(self):
        """URL for this Project's website, if set"""
        website = self.related_links.filter(type__name="Website").first()
        if website:
            return website.url

    def latest_grant(self):
        """Most recent :class:`Grant` for this Project"""
        if self.grants.count():
            return self.grants.order_by("-start_date").first()

    def current_memberships(self):
        """:class:`MembershipQueryset` of current members sorted by role"""
        # uses memberships rather than members so that we can retain role
        # information attached to the membership
        today = timezone.now().date()
        # if the last grant for this project is over, display the team
        # for that grant period
        latest_grant = self.latest_grant()
        if latest_grant and latest_grant.end_date and \
           latest_grant.end_date < today:
            return self.memberships \
                .filter(start_date__lte=latest_grant.end_date) \
                .filter(
                    models.Q(end_date__gte=latest_grant.start_date) |
                    models.Q(end_date__isnull=True)
                )

        # otherwise, return current members based on date
        return self.memberships.filter(start_date__lte=today) \
            .filter(
                models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)
        )

    def alums(self):
        """:class:`PersonQueryset` of past members sorted by last name"""
        # uses people rather than memberships so that we can use distinct()
        # to ensure people aren't counted multiple times for each grant
        # and because we don't care about role (always 'alum')
        return self.members \
            .distinct() \
            .exclude(membership__in=self.current_memberships()) \
            .order_by("last_name")


class GrantType(models.Model):
    '''Model to track kinds of grants'''
    grant_type = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.grant_type


class Grant(DateRange):
    '''A specific grant associated with a project'''
    project = ParentalKey(
        Project, null=True, on_delete=models.CASCADE, related_name="grants")
    old_project = models.ForeignKey(
        OldProject, null=True, editable=False, on_delete=models.SET_NULL)
    grant_type = models.ForeignKey(GrantType, on_delete=models.CASCADE)

    class Meta:
        ordering = ['start_date', 'project']

    def __str__(self):
        return '%s: %s (%s)' % (self.project.title, self.grant_type.grant_type,
                                self.years)


class Role(models.Model):
    '''A role on a project'''
    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False,
                                             null=False)

    class Meta:
        ordering = ['sort_order']

    def __str__(self):
        return self.title


class Membership(DateRange):
    '''Project membership - joins project, user, and role.'''
    project = ParentalKey(Project, on_delete=models.CASCADE, null=True,
                          related_name="memberships")
    old_project = models.ForeignKey(
        OldProject, null=True, editable=False, on_delete=models.SET_NULL)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        ordering = ('role__sort_order', 'person__last_name')

    def __str__(self):
        return '%s - %s on %s (%s)' % (self.person, self.role,
                                       self.project, self.years)


class ProjectRelatedLink(RelatedLink):
    '''Through-model for associating projects with relatedlinks'''
    project = ParentalKey(
        Project, on_delete=models.CASCADE, related_name="related_links")
    old_project = models.ForeignKey(
        OldProject, null=True, editable=False, on_delete=models.SET_NULL)

    def __str__(self):
        return "%s – %s (%s)" % (self.person, self.type, self.display_url)


class ProjectsLandingPage(LandingPage):
    """LandingPage subtype for Projects that holds Project pages."""
    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a Project; this is so that
    # Projects made in the admin automatically are created here.
    subpage_types = [Project]
    # use the regular landing page template
    template = LandingPage.template
