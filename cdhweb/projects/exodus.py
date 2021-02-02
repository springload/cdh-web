"""Exodus script for projects"""

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.pages.exodus import convert_slug, get_wagtail_image, to_streamfield
from cdhweb.projects.models import OldProject, Project, ProjectsLandingPage


def project_exodus():
    """exodize all project models"""
    # if no project landing page, nothing to do
    project_landing = ProjectsLandingPage.objects.first()
    if not project_landing:
        return

    # create new project pages
    for project in OldProject.objects.all():
        # create project page
        project_page = Project(
            title=project.title,
            slug=convert_slug(project.slug),
            image=get_wagtail_image(project.image),
            thumbnail=get_wagtail_image(project.thumb),
            highlight=project.highlight,
            cdh_built=project.cdh_built,
            working_group=project.working_group,
            short_description=project.short_description,
            long_description=to_streamfield(project.long_description)
        )

        # add it as child of project landing page so slugs are correct
        project_landing.add_child(instance=project_page)
        project_landing.save()

        # if the old project wasn't published, unpublish the new one
        if project.status != CONTENT_STATUS_PUBLISHED:
            project_page.unpublish()

        # transfer memberships
        for membership in project.membership_set.all():
            membership.project = project_page
            membership.save()

        # transfer grants
        for grant in project.grant_set.all():
            grant.project = project_page
            grant.save()

        # transfer related links
        for link in project.projectrelatedlink_set.all():
            link.project = project_page
            link.save()

        # NOTE no tags to migrate
        # TODO transfer attachments
