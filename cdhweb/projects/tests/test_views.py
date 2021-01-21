from datetime import timedelta, datetime
from unittest import TestCase, skip

from cdhweb.projects.models import Project, Grant, GrantType, ProjectRelatedLink
from cdhweb.pages.models import RelatedLinkType

@skip("todo")
class TestViews(TestCase):

    def test_list(self):
        # create test project
        proj = Project.objects.create(title="Derrida's Margins")
        # add a grant that is current (has not ended)
        today = datetime.today()
        grtype = GrantType.objects.create(grant_type='Sponsored Project')
        Grant.objects.create(project=proj, grant_type=grtype,
                             start_date=today - timedelta(days=30),
                             end_date=today + timedelta(days=30))

        response = self.client.get(reverse('project:list'))
        assert proj in response.context['project_list']
        self.assertContains(response, escape(proj.title))
        self.assertContains(response, proj.get_absolute_url())
        self.assertContains(response, proj.short_description)
        # no external link
        self.assertNotContains(
            response, '<a class="external" title="Project Website"')
        # no 'built by cdh' flag
        self.assertNotContains(response, 'Built by CDH')

        # add link, set as built by cdh
        website = RelatedLinkType.objects.get(name='Website')
        project_url = 'http://derridas-margins.princeton.edu'
        ProjectRelatedLink.objects.create(project=proj, type=website,
                                       url=project_url)
        proj.cdh_built = True
        proj.save()
        response = self.client.get(reverse('project:list'))
        self.assertContains(
            response, '<a class="external" title="Project Website"')
        self.assertContains(response, project_url)
        self.assertContains(response, 'Built by CDH')

        # check past projects
        proj = Project.objects.create(title="Derrida's Margins")
        response = self.client.get(reverse('project:list'))
        assert proj not in response.context['project_list']
        assert proj in response.context['past_projects']

        # TODO: test thumbnail image?

    def test_staff_list(self):
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

        response = self.client.get(reverse('project:staff'))
        # sponsored project not on staff page
        self.assertNotContains(response, other_proj.get_absolute_url())

        # staff & post-doc projects are displayed
        self.assertContains(response, staff_proj.title)
        self.assertContains(response, staff_proj.get_absolute_url())
        self.assertContains(response, postdoc_proj.title)
        self.assertContains(response, postdoc_proj.get_absolute_url())

        # not testing display specifics since re-used from main project list

    def test_working_group_list(self):
        # create a working group
        wg = Project.objects.create(
            title="My DH Working Group", working_group=True)
        derrida, _ = Project.objects.get_or_create(title="Derrida's Margins")

        response = self.client.get(reverse('project:working-groups'))
        # sponsored project not on working group page
        self.assertNotContains(response, derrida.get_absolute_url())

        # working group is displayed
        self.assertContains(response, wg.title)
        self.assertContains(response, wg.get_absolute_url())

        # working groups page shouldn't have a "past projects" section
        self.assertNotContains(response, "Past Projects")

        # create a grant for the working group that ended in the past
        start = datetime.today() - timedelta(days=120)
        end = datetime.today() - timedelta(days=30)
        seed, _ = GrantType.objects.get_or_create(grant_type='Seed')
        Grant.objects.create(project=wg, grant_type=seed,
                             start_date=start, end_date=end)

        # still shouldn't have a "past projects" section
        self.assertNotContains(response, "Past Projects")

    @skip("fixme")
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
            Membership(project=proj, person=contrib1, role=consult, start_date=grant.start_date),
            Membership(project=proj, person=contrib2, role=consult, start_date=grant.start_date),
            Membership(project=proj, person=contrib3, role=pi, start_date=grant.start_date)
        ])
        # add a website url
        website = RelatedLinkType.objects.get(name='Website')
        project_url = 'http://something.princeton.edu'
        ProjectRelatedLink.objects.create(project=proj, type=website,
                                       url=project_url)

        response = self.client.get(reverse('project:detail',
                                           kwargs={'slug': proj.slug}))
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
        self.assertContains(response, project_url)

        # test grant dates displayed
        self.assertContains(response, '<h2>CDH Grant History</h2>')
        self.assertContains(response,
                            '%s %s' % (grant.years, grant.grant_type))

        # if for some reason a project has no grants, should not display grants
        proj.grant_set.all().delete()
        response = self.client.get(reverse('project:detail',
                                           kwargs={'slug': proj.slug}))
        self.assertNotContains(response, '<h2>CDH Grant History</h2>')

        # TODO: test large image included