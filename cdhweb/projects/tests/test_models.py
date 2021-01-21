from unittest import skip
from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone
from django.utils.html import escape
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)

from cdhweb.people.models import Profile
from cdhweb.projects.models import (Grant, GrantType, Membership, Project,
                                    ProjectRelatedLink, Role)
from cdhweb.projects.sitemaps import ProjectSitemap
from cdhweb.pages.models import RelatedLinkType


class TestGrantType(TestCase):

    def test_str(self):
        grtype = GrantType(grant_type='Sponsored Project')
        assert str(grtype) == grtype.grant_type


class TestRole(TestCase):

    def test_str(self):
        role = Role(title='Principal Investigator')
        assert str(role) == role.title

@skip("todo")
class TestProjectQuerySet(TestCase):

    def test_highlighted(self):
        proj = Project.objects.create(title="Derrida's Margins")

        assert not Project.objects.highlighted().exists()

        proj.highlight = True
        proj.save()
        assert Project.objects.highlighted().exists()

    def test_current(self):
        today = datetime.today()
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=today - timedelta(days=2),
                                     end_date=today - timedelta(days=1))

        assert not Project.objects.current().exists()

        # grant ends in the future
        grant.end_date = today + timedelta(days=1)
        grant.save()
        assert Project.objects.current().exists()

        # grant end date is not set
        grant.end_date = None
        grant.save()
        assert Project.objects.current().exists()

    def test_not_current(self):
        today = datetime.today()
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=today - timedelta(days=2),
                                     end_date=today - timedelta(days=1))

        assert Project.objects.not_current().exists()

        # grant end date in the future
        grant.end_date = today + timedelta(days=1)
        grant.save()
        assert not Project.objects.not_current().exists()

        # grant end date is not set
        grant.end_date = None
        grant.save()
        assert not Project.objects.not_current().exists()

    def test_staff_or_postdoc(self):
        # create staff, postdoc, and other project
        start = datetime.today() - timedelta(days=30)
        staff_proj = Project.objects.create(title="Pliny Project")
        staff_rd = GrantType.objects.get_or_create(grant_type='Staff R&D')[0]
        Grant.objects.create(project=staff_proj, grant_type=staff_rd,
                             start_date=start)
        postdoc_proj = Project.objects.create(
            title="Linked Global Networks of Cultural Production")
        postdoc_grant = GrantType.objects.get_or_create(
            grant_type='Postdoctoral Research Project')[0]
        Grant.objects.create(project=postdoc_proj, grant_type=postdoc_grant,
                             start_date=start)
        other_proj = Project.objects.create(title="Derrida's Margins")

        staff_postdoc_projects = Project.objects.staff_or_postdoc()
        assert staff_proj in staff_postdoc_projects
        assert postdoc_proj in staff_postdoc_projects
        assert other_proj not in staff_postdoc_projects

    def test_not_staff_or_postdoc(self):
        # create staff, postdoc, and other project
        start = datetime.today() - timedelta(days=30)
        staff_proj = Project.objects.create(title="Pliny Project")
        staff_rd = GrantType.objects.get_or_create(grant_type='Staff R&D')[0]
        Grant.objects.create(project=staff_proj, grant_type=staff_rd,
                             start_date=start)
        postdoc_proj = Project.objects.create(
            title="Linked Global Networks of Cultural Production")
        postdoc_grant = GrantType.objects.get_or_create(
            grant_type='Postdoctoral Research Project')[0]
        Grant.objects.create(project=postdoc_proj, grant_type=postdoc_grant,
                             start_date=start)
        other_proj = Project.objects.create(title="Derrida's Margins")

        non_staff_postdoc_projects = Project.objects.not_staff_or_postdoc()
        assert staff_proj not in non_staff_postdoc_projects
        assert postdoc_proj not in non_staff_postdoc_projects
        assert other_proj in non_staff_postdoc_projects

    def test_order_by_newest_grant(self):
        # create three test projects with grants in successive years
        sponsored = GrantType.objects.get_or_create(
            grant_type='Sponsored Project')[0]
        p1 = Project.objects.create(title="One")
        Grant.objects.create(project=p1, grant_type=sponsored,
                             start_date=date(2015, 9, 1))
        p2 = Project.objects.create(title="Two")
        Grant.objects.create(project=p2, grant_type=sponsored,
                             start_date=date(2016, 9, 1))
        p3 = Project.objects.create(title="Three")
        Grant.objects.create(project=p3, grant_type=sponsored,
                             start_date=date(2017, 9, 1))

        ordered = Project.objects.order_by_newest_grant()
        # should be ordered newest first
        assert ordered[0] == p3
        assert ordered[1] == p2
        assert ordered[2] == p1

        # with multiple grants, still orders based on newest grant
        Grant.objects.create(project=p3, grant_type=sponsored,
                             start_date=date(2015, 9, 1))

        ordered = Project.objects.order_by_newest_grant()
        # should be ordered newest first
        assert ordered[0] == p3

    def test_published(self):
        # technically a mixin method, testing here for convenience

        staffer = get_user_model().objects.create(username='staffer',
                                                  is_staff=True)
        nonstaffer = get_user_model().objects.create(username='nonstaffer',
                                                     is_staff=False)

        # careate project in draft status
        proj = Project.objects.create(title="Derrida's Margins",
                                      status=CONTENT_STATUS_DRAFT)

        # draft displayable only listed for staff user
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # set to published, no dates
        proj.status = CONTENT_STATUS_PUBLISHED
        proj.save()

        # published displayable listed for everyone
        assert proj in Project.objects.published()
        assert proj in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # publish date in future - only visible to staff user
        proj.publish_date = timezone.now() + timedelta(days=2)
        proj.save()
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # publish date in past - visible to all
        proj.publish_date = timezone.now() - timedelta(days=2)
        proj.save()
        assert proj in Project.objects.published()
        assert proj in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

        # expiration date in past - only visible to staff user
        proj.expiry_date = timezone.now() - timedelta(days=2)
        proj.save()
        assert proj not in Project.objects.published()
        assert proj not in Project.objects.published(nonstaffer)
        assert proj in Project.objects.published(staffer)

    def test_working_groups(self):
        wg = Project.objects.create(
            title="My DH Working Group", working_group=True)
        derrida = Project.objects.get_or_create(title="Derrida's Margins")

        # should include only working groups
        all_wgs = Project.objects.working_groups()
        assert wg in all_wgs
        assert derrida not in all_wgs

@skip("todo")
class TestGrant(TestCase):

    def test_str(self):
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        start_year, end_year = (2016, 2017)
        grant = Grant(project=proj, grant_type=grtype,
                      start_date=datetime(start_year, 1, 1),
                      end_date=datetime(end_year, 1, 1))
        assert str(grant) == '%s: %s (2016–2017)' % \
            (proj.title, grtype.grant_type)

@skip("todo")
class TestMembership(TestCase):

    @skip("fixme")
    def test_str(self):
        # create test objects needed for a membership
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=proj, grant_type=grtype,
                                     start_date=datetime(2016, 1, 1),
                                     end_date=datetime(2017, 1, 1))
        user = get_user_model().objects.create(username='contributor')
        role = Role.objects.create(title='Data consultant', sort_order=1)
        membership = Membership.objects.create(
            project=proj, person=user, role=role, start_date=grant.start_date)

        assert str(membership) == '%s - %s on %s (%s)' % (user, role, proj,
                                                          membership.years)

@skip("todo")
class TestProjectRelatedLink(TestCase):

    def test_display_url(self):
        base_url = 'derridas-margins.princeton.edu'
        project_url = 'http://%s' % base_url
        proj = Project.objects.create(title="Derrida's Margins")
        website = RelatedLinkType.objects.get(name='Website')
        res = ProjectRelatedLink.objects.create(project=proj, type=website,
                                             url=project_url)
        assert res.display_url() == base_url

        # https
        res.url = 'https://%s' % base_url
        assert res.display_url() == base_url
