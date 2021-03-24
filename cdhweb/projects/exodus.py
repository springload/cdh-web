"""Exodus script for projects"""
import logging

from mezzanine.core.models import CONTENT_STATUS_PUBLISHED

from cdhweb.pages.exodus import convert_slug, exodize_attachments, \
    get_wagtail_image, to_streamfield
from cdhweb.projects.models import OldProject, Project, ProjectsLandingPage


def project_exodus():
    """exodize all project models"""
    # get the top-level projects landing page
    try:
        project_landing = ProjectsLandingPage.objects.get()
    except ProjectsLandingPage.DoesNotExist:
        return

    # create new project pages
    for project in OldProject.objects.all():
        logging.debug("found mezzanine project %s" % project)

        # create project page
        project_page = Project(
            title=project.title,
            highlight=project.highlight,
            cdh_built=project.cdh_built,
            slug=convert_slug(project.slug),
            working_group=project.working_group,
            image=get_wagtail_image(project.image),
            search_description=project.description,
            thumbnail=get_wagtail_image(project.thumb),
            short_description=project.short_description,
            body=to_streamfield(project.long_description),
        )

        # add it as child of project landing page so slugs are correct
        project_landing.add_child(instance=project_page)
        project_landing.save()

        # if the old project wasn't published, unpublish the new one
        if project.status != CONTENT_STATUS_PUBLISHED:
            project_page.unpublish()

        # set publication dates
        project_page.first_published_at = project.publish_date
        project_page.last_published_at = project.updated
        project_page.save()

        # transfer memberships
        for membership in project.membership_set.all():
            membership.project = project_page
            membership.save()
            logging.debug("updated membership %s" % membership)

        # transfer grants
        for grant in project.grant_set.all():
            grant.project = project_page
            grant.save()
            logging.debug("updated grant %s" % grant)

        # transfer related links
        for link in project.projectrelatedlink_set.all():
            link.project = project_page
            link.save()
            logging.debug("updated related link %s" % link)

        # transfer attachments
        exodize_attachments(project, project_page)

        # NOTE no tags to migrate
