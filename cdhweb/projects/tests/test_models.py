import pytest
from datetime import date, datetime, timedelta

from cdhweb.pages.models import RelatedLinkType
from cdhweb.projects.models import (Grant, GrantType, Membership, Project,
                                    ProjectRelatedLink, Role)
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from mezzanine.core.models import (CONTENT_STATUS_DRAFT,
                                   CONTENT_STATUS_PUBLISHED)


class TestGrantType:

    def test_str(self):
        grtype = GrantType(grant_type='Sponsored Project')
        assert str(grtype) == grtype.grant_type


class TestRole:

    def test_str(self):
        role = Role(title='Principal Investigator')
        assert str(role) == role.title


@pytest.mark.django_db
class TestProjectQuerySet:

    def test_highlighted(self, derrida):
        """should query highlighted projects"""
        # derrida isn't highlighted
        assert not Project.objects.highlighted().exists()
        # highlight it, should be returned
        derrida.highlight = True
        derrida.save()
        assert Project.objects.highlighted().exists()

    def test_current(self, derrida):
        """should query projects with current grant"""
        # derrida latest grant ends today; should be current
        assert Project.objects.current().exists()
        grant = derrida.latest_grant()

        # future end date should also be current
        grant.end_date = datetime.today() + timedelta(days=50)
        grant.save()
        assert Project.objects.current().exists()

        # no end date should also be current
        grant.end_date = None
        grant.save()
        assert Project.objects.current().exists()

        # past end date should not be current
        grant.end_date = datetime.today() - timedelta(days=50)
        grant.save()
        assert not Project.objects.current().exists()

    def test_not_current(self, derrida):
        """should query projects with no current grant"""
        # derrida latest grant ends today; should not be not current
        assert not Project.objects.not_current().exists()
        grant = derrida.latest_grant()

        # future end date should also be current
        grant.end_date = datetime.today() + timedelta(days=50)
        grant.save()
        assert not Project.objects.not_current().exists()

        # no end date should also be current
        grant.end_date = None
        grant.save()
        assert not Project.objects.not_current().exists()

        # past end date should not be current
        grant.end_date = datetime.today() - timedelta(days=50)
        grant.save()
        assert Project.objects.not_current().exists()

    def test_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query staff or postdoc projects"""
        staff_postdoc_projects = Project.objects.staff_or_postdoc()
        assert pliny in staff_postdoc_projects          # staff r&d
        assert ocampo in staff_postdoc_projects         # postdoc
        assert derrida not in staff_postdoc_projects    # sponsored
        assert slavic not in staff_postdoc_projects     # working group

    def test_not_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query non-staff or postdoc projects"""
        non_staff_postdoc_projects = Project.objects.not_staff_or_postdoc()
        assert derrida in non_staff_postdoc_projects        # sponsored
        assert slavic not in non_staff_postdoc_projects     # working group
        assert pliny not in non_staff_postdoc_projects      # staff r&d
        assert ocampo not in non_staff_postdoc_projects     # postdoc

    def test_not_staff_or_postdoc(self, derrida, pliny, ocampo, slavic):
        """should query working groups"""
        working_groups = Project.objects.working_groups()
        assert slavic in working_groups         # working group
        assert derrida not in working_groups    # sponsored
        assert pliny not in working_groups      # staff r&d
        assert ocampo not in working_groups     # postdoc

    def test_order_by_newest_grant(self, derrida, pliny, ocampo, slavic):
        """should order projects by latest grant"""
        ordered = Project.objects.order_by_newest_grant()
        assert ordered[0] == derrida    # RPG started 1yr ago
        assert ordered[1] == pliny      # started 400 days ago
        assert ordered[2] == ocampo     # started 450 days ago
        assert ordered[3] == slavic     # seed grant 2yrs ago


@pytest.mark.skip
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


@pytest.mark.skip
class TestMembership(TestCase):

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


@pytest.mark.skip
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
