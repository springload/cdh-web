import string
from datetime import timedelta

from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from cdhweb.events.models import Event, EventType
from cdhweb.projects.models import Project, GrantType, Grant


class TestViews(TestCase):

    def test_site_index(self):
        index_url = reverse('home')

        # should not error even if no events/projects to display
        response = self.client.get(index_url)
        assert response.status_code == 200

        # test how projects are displayed on the home page
        today = timezone.now()
        site = Site.objects.first()
        projects = Project.objects.bulk_create(
            [Project(title=n, slug=n, is_active=True, site=site)
             for n in string.ascii_letters[:5]]
        )
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        # add grant that covers the current date
        grant_start = today - timedelta(days=2)
        grant_end = today + timedelta(days=7)
        Grant.objects.bulk_create(
            [Grant(project=proj, grant_type=grtype,
                   start_date=grant_start, end_date=grant_end)
             for proj in Project.objects.all()]
        )

        response = self.client.get(index_url)
        # should be 4 random projects in context
        assert len(response.context['projects']) == 4

        # test that current and active is honored
        # - delete one project so that all four will be present
        Project.objects.first().delete()
        # get next project and mark inactive
        inactive_proj = Project.objects.first()
        inactive_proj.is_active = False
        inactive_proj.save()
        response = self.client.get(index_url)
        assert inactive_proj not in response.context['projects']

        # get next active project and remove grant
        noncurrent_proj = Project.objects.active().first()
        noncurrent_proj.grant_set.all().delete()
        response = self.client.get(index_url)
        assert noncurrent_proj not in response.context['projects']
