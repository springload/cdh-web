from wagtail.test.utils import WagtailPageTestCase

from cdhweb.pages.models import LinkPage, RelatedLinkType
from cdhweb.people.models import Person
from cdhweb.projects.models import (
    Grant,
    GrantType,
    Project,
    ProjectRelatedLink,
    ProjectsLandingPage,
    ProjectsLandingPageArchived,
)


class TestProject:
    def test_str(self, derrida):
        """project should use title for string display"""
        assert str(derrida) == "Derrida's Margins"

    def test_website_url(self, derrida):
        """project should return website URL if one is set via related link"""
        # add a website URL
        website = RelatedLinkType.objects.get_or_create(name="Website")[0]
        derrida_url = "http://derridas-margins.princeton.edu"
        ProjectRelatedLink.objects.create(
            project=derrida, type=website, url=derrida_url
        )
        assert derrida.website_url == derrida_url

    def test_latest_grant(self, derrida):
        """project should return its most recent grant"""
        # should return current RPG, not old DCG
        rpg = GrantType.objects.get(grant_type="Research Partnership")
        assert derrida.latest_grant() == Grant.objects.get(
            project=derrida, grant_type=rpg
        )

    def test_current_memberships(self, derrida):
        """project should return its current team members"""
        # should return team from first grant plus old members who stayed on
        katie = Person.objects.get(first_name="Katie", last_name="Chenoweth")
        rsk = Person.objects.get(first_name="Rebecca", last_name="Koeser")
        rm = Person.objects.get(first_name="Rebecca", last_name="Munson")
        chloe = Person.objects.get(first_name="Chloe", last_name="Vettier")
        renee = Person.objects.get(first_name="Renee", last_name="Altergott")
        current_members = [m.person for m in derrida.current_memberships()]
        assert katie in current_members
        assert rsk in current_members
        assert rm not in current_members
        assert chloe in current_members
        assert renee in current_members

    def test_alums(self, derrida):
        """project should return past team members (alums)"""
        # should return only people who are not currently on project
        katie = Person.objects.get(first_name="Katie", last_name="Chenoweth")
        rsk = Person.objects.get(first_name="Rebecca", last_name="Koeser")
        rm = Person.objects.get(first_name="Rebecca", last_name="Munson")
        chloe = Person.objects.get(first_name="Chloe", last_name="Vettier")
        renee = Person.objects.get(first_name="Renee", last_name="Altergott")
        alums = derrida.alums()
        assert katie not in alums
        assert rsk not in alums
        assert rm in alums
        assert chloe not in alums
        assert renee not in alums

    def test_sitemap(self, rf, derrida):
        """project should increase sitemap priority if built by cdh with site"""
        # project not built by cdh and without site doesn't set priority
        request = rf.get(derrida.get_url())
        sitemap_urls = derrida.get_sitemap_urls(request=request)
        assert "priority" not in sitemap_urls[0]
        # built by cdh gets slightly increased priority (0.6)
        derrida.cdh_built = True
        derrida.save()
        sitemap_urls = derrida.get_sitemap_urls(request=request)
        assert sitemap_urls[0]["priority"] == 0.6
        # having a website also gets slightly increased priority (0.6)
        derrida.cdh_built = False
        derrida.save()
        website = RelatedLinkType.objects.get_or_create(name="Website")[0]
        ProjectRelatedLink.objects.create(
            project=derrida, type=website, url="https://derridas-margins.princeton.edu"
        )
        sitemap_urls = derrida.get_sitemap_urls(request=request)
        assert sitemap_urls[0]["priority"] == 0.6
        # having both site and cdh built gets highest priority (0.7)
        derrida.cdh_built = True
        derrida.save()
        sitemap_urls = derrida.get_sitemap_urls(request=request)
        assert sitemap_urls[0]["priority"] == 0.7


class TestProjectPage(WagtailPageTestCase):
    def test_parent_pages(self):
        """project can only be created under projects link page"""
        self.assertAllowedParentPageTypes(
            Project, [ProjectsLandingPageArchived, ProjectsLandingPage]
        )

    def test_subpages(self):
        """project page can't have children"""
        self.assertAllowedSubpageTypes(Project, [])


class TestProjectsLandingPageArchived(WagtailPageTestCase):
    def test_parentpage_types(self):
        """projects link page should not be creatable in admin"""
        self.assertAllowedParentPageTypes(ProjectsLandingPageArchived, [])

    def test_subpage_types(self):
        """projects link page only allowed child is project page"""
        self.assertAllowedSubpageTypes(ProjectsLandingPageArchived, [Project, LinkPage])
