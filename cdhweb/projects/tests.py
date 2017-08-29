from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import resolve

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

