from datetime import date, timedelta

from django.urls import reverse
from pytest_django.asserts import (assertContains, assertNotContains,
                                   assertTemplateUsed)

from cdhweb.pages.exodus import to_streamfield
from cdhweb.pages.models import PageIntro, RelatedLinkType
from cdhweb.projects.models import ProjectRelatedLink


class TestProjectDetail:

    def test_related_links(self, client, derrida):
        """project detail page should display project related links"""
        # add a github link for derrida
        github = RelatedLinkType.objects.get_or_create(name="GitHub")[0]
        derrida_gh = ProjectRelatedLink.objects.create(
            project=derrida, type=github, url="https://github.com/princeton-CDH/derrida-django")

        # should display link type and create a link using URL
        response = client.get(derrida.get_url())
        assertContains(response, '<a href="%s">GitHub</a>' %
                       derrida_gh.url, html=True)

    def test_website_url(self, client, derrida):
        """project detail page should display website url if set"""
        # create a website URL for derrida
        website = RelatedLinkType.objects.get_or_create(name="Website")[0]
        derrida_site = ProjectRelatedLink.objects.create(
            project=derrida, type=website, url="https://derridas-margins.princeton.edu")

        # should display "Project Website" as well as full URL inside link
        response = client.get(derrida.get_url())
        assertContains(response, '<a href="%s">' % derrida_site.url)
        assertContains(response, '<span>Project Website</span>', html=True)
        assertContains(response, '<span class="url">%s</span>' %
                       derrida_site.display_url, html=True)

    def test_contributors(self, client, derrida):
        """project detail page should display current project team and alums"""
        # get all memberships
        pi = derrida.memberships.get(person__first_name="Katie")
        dev = derrida.memberships.get(person__last_name="Koeser")
        pm1 = derrida.memberships.get(person__last_name="Munson")
        grad = derrida.memberships.get(person__first_name="Chloe")
        pm2 = derrida.memberships.get(person__first_name="Renee")

        # all current members and their roles are listed exactly once
        response = client.get(derrida.get_url())
        for member in [pi, dev, grad, pm2]:
            assertContains(response, member.person, count=1)
            assertContains(response, member.role, count=1)

        # pm1 should be listed in alums (actually "Alum" since singular)
        assertContains(response, "Project Alum")
        assertContains(response, pm1.person)

    def test_grants(self, client, derrida):
        """project detail page should display all grants"""
        # get all grants
        dcg = derrida.grants.get(grant_type__grant_type="Dataset Curation")
        rpg = derrida.grants.get(grant_type__grant_type="Research Partnership")

        # should display with years
        response = client.get(derrida.get_url())
        assertContains(response, "CDH Grant History")
        assertContains(response, "%s Dataset Curation" % dcg.years)
        assertContains(response, "%s Research Partnership" % rpg.years)

    def test_long_description(self, client, derrida):
        """project detail page should display long description if set"""
        # set a long description for derrida
        derrida.long_description = to_streamfield("<b>About Derrida</b>")
        derrida.save()

        # should display with rich text
        response = client.get(derrida.get_url())
        assertContains(response, "<b>About Derrida</b>", html=True)


class TestProjectLists:

    def test_page_titles(self, client, projects):
        """project list pages should show title and past title as headings"""
        # sponsored projects (none currently past)
        response = client.get(reverse("projects:sponsored"))
        assertContains(response, "<h1>Sponsored Projects</h1>")
        assertNotContains(response, "<h2>Past Projects</h2>")

        # staff & postdoc projects (none currently past)
        response = client.get(reverse("projects:staff"))
        assertContains(response, "<h1>Staff Projects</h1>")
        assertNotContains(response, "<h2>Past Projects</h2>")

        # working groups (no past shown)
        response = client.get(reverse("projects:working-groups"))
        assertContains(response, "<h1>DH Working Groups</h1>")
        assertNotContains(response, "<h2>Past Projects</h2>")

        # make all projects past: delete all grants except latest; end yesterday    
        for _, project in projects.items():
            grant = project.latest_grant()
            project.grants.exclude(pk=grant.pk).delete()
            grant.end_date = date.today() - timedelta(days=1)
            grant.save()

        # sponsored projects, past section should display
        response = client.get(reverse("projects:sponsored"))
        assertContains(response, "<h2>Past Projects</h2>")

        # staff & postdoc projects, past section should display
        response = client.get(reverse("projects:staff"))
        assertContains(response, "<h2>Past Projects</h2>")

        # working groups should never be past, even if grant is
        response = client.get(reverse("projects:working-groups"))
        assertNotContains(response, "<h2>Past Projects</h2>")

    def test_page_intro(self, client, projects_link_page):
        """project list pages should display an intro snippet if set"""
        # create a snippet for the sponsored projects page
        PageIntro.objects.create(page=projects_link_page,
                                 paragraph="<i>test content</i>")

        # visit and check that it renders
        response = client.get(reverse("projects:sponsored"))
        assertContains(response, "<i>test content</i>")

    def test_project_card(self, client, projects):
        """project list pages should display cards for each project"""
        # one project card for each staff/postdoc project
        response = client.get(reverse("projects:staff"))
        assertTemplateUsed("projects/snippets/project_card.html")
        assertContains(response, '<div class="card project', count=2)

        # card contains link to project page, title, and short description
        assertContains(response, '<a href="%s">' % projects["pliny"].get_url())
        assertContains(response, '<a href="%s">' %
                       projects["ocampo"].get_url())
        assertContains(response, '<h2>%s</h2>' % projects["pliny"].title)
        assertContains(response, '<h2>%s</h2>' % projects["ocampo"].title)
        assertContains(response, '<p>%s</p>' %
                       projects["pliny"].short_description)
        assertContains(response, '<p>%s</p>' %
                       projects["ocampo"].short_description)
