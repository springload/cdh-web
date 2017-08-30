from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.html import escape
import pytest

from cdhweb.people.models import Profile
from cdhweb.projects.models import Grant, GrantType, Project, Role, \
    Membership


class TestGrantType(TestCase):

    def test_str(self):
        grtype = GrantType(grant_type='Sponsored Project')
        assert str(grtype) == grtype.grant_type


class TestRole(TestCase):

    def test_str(self):
        role = Role(title='Principal Investigator')
        assert str(role) == role.title


class TestProject(TestCase):

    def test_str(self):
        proj = Project(title="Derrida's Margins")
        assert str(proj) == proj.title

    def test_get_absolute_url(self):
        proj = Project(title="Mapping Expatriate Paris", slug="mep")
        resolved_url = resolve(proj.get_absolute_url())
        assert resolved_url.namespace == 'project'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['slug'] == proj.slug


class TestProjectQuerySet(TestCase):

    def test_active(self):
        proj = Project.objects.create(title="Derrida's Margins")

        assert not Project.objects.active().exists()

        proj.is_active = True
        proj.save()
        assert Project.objects.active().exists()

    def test_current(self):
        today = datetime.today()
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
            start_date=today - timedelta(days=2),
            end_date=today - timedelta(days=1))

        assert not Project.objects.current().exists()

        grant.end_date = today + timedelta(days=1)
        grant.save()
        assert Project.objects.current().exists()


class TestGrant(TestCase):

    def test_str(self):
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        start_year, end_year = (2016, 2017)
        grant = Grant(project=proj, grant_type=grtype,
            start_date=datetime(start_year, 1, 1),
            end_date=datetime(end_year, 1, 1))
        assert str(grant) == '%s: %s (2016-2017)' % (proj.title, grtype.grant_type)


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
        membership = Membership.objects.create(project=proj,
            user=user, grant=grant, role=role)

        assert str(membership) == '%s - %s on %s' % (user, role, grant)


class TestMembershipQuerySet(TestCase):

    def test_current(self):
        # create test objects needed for a membership
        proj = Project.objects.create(title="Derrida's Margins")
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        today = datetime.today()
        # asocciated grant has ended
        grant = Grant.objects.create(project=proj, grant_type=grtype,
            start_date=today - timedelta(days=2),
            end_date=today - timedelta(days=1))
        user = get_user_model().objects.create(username='contributor')
        role = Role.objects.create(title='Data consultant', sort_order=1)
        membership = Membership.objects.create(project=proj,
            user=user, grant=grant, role=role)

        # should be empty
        assert not Membership.objects.current().exists()

        # update grant so date is after today
        membership.grant.end_date = today + timedelta(days=1)
        membership.grant.save()
        # should not be empty
        assert Membership.objects.current().exists()


# FIXME: skipping for now because mezzanine page_menu causes an error in tests
@pytest.mark.skip
class TestViews(TestCase):
    fixtures = ['test-pages.json']

    def test_list(self):
        proj = Project.objects.create(title="Derrida's Margins")
        response = self.client.get(reverse('project:list'))
        self.assertContains(response, escape(proj.title))
        self.assertContains(response, proj.get_absolute_url())
        self.assertContains(response, proj.short_description)
        # TODO: test thumbnail image

    def test_detail(self):
        proj = Project.objects.create(title="Derrida's Margins",
            slug='derrida', short_description='Citations and interventions',
            long_description='<p>an annotation project</p>')
        today = datetime.today()
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        grant = Grant.objects.create(project=proj, grant_type=grtype,
            start_date=today - timedelta(days=2),
            end_date=today + timedelta(days=1))
        # add project members to test contributor display
        contrib1 = get_user_model().objects.create(username='contributor one')
        contrib2 = get_user_model().objects.create(username='contributor two')
        contrib3 = get_user_model().objects.create(username='contributor three')
        site = Site.objects.first()
        Profile.objects.bulk_create([
            Profile(user=contrib1, title=contrib1.username, site=site),
            Profile(user=contrib2, title=contrib2.username, site=site),
            Profile(user=contrib3, title=contrib3.username, site=site)
        ])
        consult = Role.objects.create(title='Consultant', sort_order=2)
        pi = Role.objects.create(title='Principal Investigator', sort_order=1)
        Membership.objects.bulk_create([
            Membership(project=proj, user=contrib1, grant=grant, role=consult),
            Membership(project=proj, user=contrib2, grant=grant, role=consult),
            Membership(project=proj, user=contrib3, grant=grant, role=pi)
        ])

        response = self.client.get(reverse('project:detail',
            kwargs={'slug':  proj.slug}))
        assert response.context['project'] == proj
        self.assertContains(response, escape(proj.title))
        self.assertContains(response, proj.short_description)
        self.assertContains(response, proj.long_description)
        # contributors
        self.assertContains(response, consult.title, count=1,
            msg_prefix='contributor roles should only show up once')
        self.assertContains(response, pi.title, count=1,
            msg_prefix='contributor roles should only show up once')
        for contributor in [contrib1, contrib2, contrib3]:
            self.assertContains(response, contributor.profile.title)
        # TODO: test large image included
