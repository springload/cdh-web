from django.db import models
from django.utils import timezone
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from taggit.models import TaggedItemBase
from wagtail.admin.edit_handlers import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    StreamFieldPanel,
)
from wagtail.core.models import Page, PageManager, PageQuerySet
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index

from cdhweb.pages.models import BasePage, DateRange, LandingPage, LinkPage, RelatedLink
from cdhweb.people.models import Person


class ProjectQuerySet(PageQuerySet):
    def highlighted(self):
        """return projects that are marked as highlighted"""
        return self.filter(highlight=True)

    def _current_grant_query(self):
        """QuerySet filter to find projects with a current grant,
        based on start date before current date and end date after current
        date or not set.
        """
        today = timezone.now()
        return models.Q(grants__start_date__lt=today) & (
            models.Q(grants__end_date__gt=today)
            | models.Q(grants__end_date__isnull=True)
        )

    def current(self):
        """Projects with a current grant, based on dates"""
        return self.filter(self._current_grant_query()).distinct()

    def not_current(self):
        """Projects with no current grant, based on dates"""
        return self.exclude(self._current_grant_query())

    #: grant types that indicate staff or postdoc project
    staff_postdoc_grants = [
        "Staff R&D",
        "Staff Project",
        "Postdoctoral Research Project",
    ]

    def staff_or_postdoc(self):
        """Staff and postdoc projects, based on grant type"""
        return self.filter(
            grants__grant_type__grant_type__in=self.staff_postdoc_grants
        ).exclude(working_group=True)

    def not_staff_or_postdoc(self):
        """Exclude staff and postdoc projects, based on grant type"""
        return self.exclude(
            grants__grant_type__grant_type__in=self.staff_postdoc_grants
        ).exclude(working_group=True)

    def working_groups(self):
        """Include only projects with the working group flag set"""
        return self.filter(working_group=True)

    def order_by_newest_grant(self):
        """order by grant start date, most recent grants first; secondary
        sort by project title"""
        # NOTE: using annotation to get just the most recent start date
        # to avoid issues with projects appearing multiple times.
        return self.annotate(last_start=models.Max("grants__start_date")).order_by(
            "-last_start", "title"
        )


# custom manager for wagtail pages, see:
# https://docs.wagtail.io/en/stable/topics/pages.html#custom-page-managers
ProjectManager = PageManager.from_queryset(ProjectQuerySet)


class ProjectTag(TaggedItemBase):
    """Tags for Project pages."""

    content_object = ParentalKey(
        "projects.Project", on_delete=models.CASCADE, related_name="tagged_items"
    )


class Project(BasePage, ClusterableModel):
    """Page type for a CDH sponsored project or working group."""

    short_description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Brief tagline for display on project card in browse view",
    )
    highlight = models.BooleanField(
        default=False,
        help_text="Include in randomized project display on the home page.",
    )
    cdh_built = models.BooleanField(
        "CDH Built",
        default=False,
        help_text="Project built by CDH Development & Design team.",
    )
    working_group = models.BooleanField(
        "Working Group",
        default=False,
        help_text="Project is a long-term collaborative group associated with the CDH.",
    )
    image = models.ForeignKey(
        "wagtailimages.image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image for display on project detail page (optional)",
    )
    thumbnail = models.ForeignKey(
        "wagtailimages.image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Image for display on project card (optional)",
    )
    members = models.ManyToManyField(Person, through="Membership")
    tags = ClusterTaggableManager(through=ProjectTag, blank=True)
    # TODO attachments (#245)

    # can only be created underneath project landing page
    parent_page_types = ["projects.ProjectsLandingPage"]
    # no allowed subpages
    subpage_types = []

    # admin edit configuration
    content_panels = Page.content_panels + [
        FieldRowPanel(
            (
                FieldPanel("highlight"),
                FieldPanel("cdh_built"),
                FieldPanel("working_group"),
            ),
            "Settings",
        ),
        FieldRowPanel(
            (ImageChooserPanel("thumbnail"), ImageChooserPanel("image")), "Images"
        ),
        FieldPanel("short_description"),
        StreamFieldPanel("body"),
        InlinePanel("related_links", label="Links"),
        InlinePanel(
            "grants",
            panels=[
                FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date"))),
                FieldPanel("grant_type"),
            ],
            label="Grants",
        ),
        InlinePanel(
            "memberships",
            panels=[
                FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date"))),
                FieldPanel("person"),
                FieldPanel("role"),
            ],
            label="Members",
        ),
        StreamFieldPanel("attachments"),
    ]
    promote_panels = Page.promote_panels + [FieldPanel("tags")]

    # custom manager/queryset logic
    objects = ProjectManager()

    # search fields
    search_fields = BasePage.search_fields + [
        index.SearchField("short_description"),
        index.RelatedFields(
            "members",
            [
                index.SearchField("first_name"),
                index.SearchField("last_name"),
            ],
        ),
    ]

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
        # NOTE memberships is a FakeQuerySet from modelcluster.ParentalKey when
        # the page is being previewed in wagtail, so Q lookups are not possible.
        # see: https://github.com/wagtail/django-modelcluster/issues/121
        memberships = Membership.objects.filter(project__pk=self.pk)
        # uses memberships rather than members so that we can retain role
        # information attached to the membership
        today = timezone.now().date()
        # if the last grant for this project is over, display the team
        # for that grant period
        latest_grant = self.latest_grant()
        if latest_grant and latest_grant.end_date and latest_grant.end_date < today:
            return memberships.filter(start_date__lte=latest_grant.end_date).filter(
                models.Q(end_date__gte=latest_grant.start_date)
                | models.Q(end_date__isnull=True)
            )

        # otherwise, return current members based on date
        return memberships.filter(start_date__lte=today).filter(
            models.Q(end_date__gte=today) | models.Q(end_date__isnull=True)
        )

    def alums(self):
        """:class:`PersonQueryset` of past members sorted by last name"""
        # uses people rather than memberships so that we can use distinct()
        # to ensure people aren't counted multiple times for each grant
        # and because we don't care about role (always 'alum')
        return (
            self.members.distinct()
            .exclude(membership__in=self.current_memberships())
            .order_by("last_name")
        )

    def get_sitemap_urls(self, request):
        """Override sitemap to prioritize projects built by CDH with a website."""
        # output is a list of dict; there should only ever be one element. see:
        # https://docs.wagtail.io/en/stable/reference/contrib/sitemaps.html#urls
        urls = super().get_sitemap_urls(request=request)
        if self.website_url and self.cdh_built:
            urls[0]["priority"] = 0.7
        elif self.website_url or self.cdh_built:
            urls[0]["priority"] = 0.6
        return urls


class GrantType(models.Model):
    """Model to track kinds of grants"""

    grant_type = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.grant_type


class Grant(DateRange):
    """A specific grant associated with a project"""

    project = ParentalKey(Project, on_delete=models.CASCADE, related_name="grants")
    grant_type = models.ForeignKey(GrantType, on_delete=models.CASCADE)

    class Meta:
        ordering = ["start_date", "project"]

    def __str__(self):
        return "%s: %s (%s)" % (
            self.project.title,
            self.grant_type.grant_type,
            self.years,
        )


class Role(models.Model):
    """A role on a project"""

    title = models.CharField(max_length=255, unique=True)
    sort_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        ordering = ["sort_order"]

    def __str__(self):
        return self.title

    def __lt__(self, other):
        # NOTE we need to order Memberships using role sort order by default,
        # but modelcluster doesn't support ordering via related lookups, so
        # we can't order by role__sort_order on Membership. Instead we do this.
        # see: https://github.com/wagtail/django-modelcluster/issues/45
        return self.sort_order < other.sort_order


class Membership(DateRange):
    """Project membership - joins project, user, and role."""

    project = ParentalKey(Project, on_delete=models.CASCADE, related_name="memberships")
    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        ordering = ("role", "person")

    # admin edit configuration
    panels = [
        FieldRowPanel((FieldPanel("start_date"), FieldPanel("end_date")), "Dates"),
        FieldPanel("person"),
        FieldPanel("role"),
        FieldPanel("project"),
    ]

    def __str__(self):
        return "%s - %s on %s (%s)" % (self.person, self.role, self.project, self.years)


class ProjectRelatedLink(RelatedLink):
    """Through-model for associating projects with relatedlinks"""

    project = ParentalKey(
        Project, on_delete=models.CASCADE, related_name="related_links"
    )

    def __str__(self):
        return "%s – %s (%s)" % (self.project, self.type, self.display_url)


class ProjectsLandingPage(LandingPage):
    """Container page that defines where Project pages can be created."""

    # NOTE this page can't be created in the page editor; it is only ever made
    # via a script or the console, since there's only one.
    parent_page_types = []
    # NOTE the only allowed child page type is a Project; this is so that
    # Projects made in the admin automatically are created here.
    subpage_types = [Project, LinkPage]
    # use the regular landing page template
    template = LandingPage.template
