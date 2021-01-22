from cdhweb.projects.models import Project
from cdhweb.resources.views import LastModifiedListMixin
from django.urls import reverse
from django.views.generic.list import ListView


class ProjectListView(ListView, LastModifiedListMixin):
    """Base class for project list views."""

    model = Project

    #: title for this category of projects
    page_title = "Projects"
    #: title for past projects in this category of projects
    past_title = "Past Projects"

    def get_queryset(self):
        """Get all published projects ordered by newest grant."""
        return super().get_queryset().live().order_by_newest_grant().distinct()

    def get_current(self):
        """Get current projects from the queryset. Override to customize which
        filter is used."""
        return self.object_list.current()

    def get_past(self):
        """Get past projects from the queryset. Override to customize which
        filter is used."""
        return self.object_list.not_current()

    def get_context_data(self, *args, **kwargs):
        """Add projects, titles, and navigation to context."""
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "current": self.get_current(),
            "past": self.get_past(),
            "title": self.page_title,
            "past_title": self.past_title,
            "archive_nav_urls": (
                ("Projects", reverse("projects:list")),
                ("Staff Projects", reverse("projects:staff")),
                ("DH Working Groups", reverse("projects:working-groups")),
            )
        })
        return context


class SponsoredProjectListView(ProjectListView):
    """Main project list, i.e. not staff/postdoc/working group."""

    def get_queryset(self):
        """Get all published sponsored projects."""
        return super().get_queryset().not_staff_or_postdoc()


class StaffProjectListView(ProjectListView):
    """Staff and postdoc projects, based on grant type."""

    page_title = "Staff and Postdoctoral Fellow Projects"

    def get_queryset(self):
        """Get all published staff/postdoc projects."""
        return super().get_queryset().staff_or_postdoc()


class WorkingGroupListView(ProjectListView):
    """DH Working group list, based on working group project flag."""

    page_title = "DH Working Groups"
    past_title = "Past Working Groups"

    def get_queryset(self):
        """Get all published DH working groups."""
        return Project.objects.working_groups()
