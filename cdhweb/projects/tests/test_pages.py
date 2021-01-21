from datetime import date

import pytest
from cdhweb.pages.models import RelatedLinkType
from cdhweb.projects.models import Grant, GrantType, ProjectRelatedLink
from cdhweb.people.models import Person


@pytest.mark.django_db
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
            project=derrida, type=website, url=derrida_url)
        assert derrida.website_url == derrida_url

    def test_latest_grant(self, derrida):
        """project should return its most recent grant"""
        # should return 2016-2017 RPG
        rpg = GrantType.objects.get(grant_type="Research Partnership")
        assert derrida.latest_grant() == Grant.objects.get(project=derrida, grant_type=rpg, start_date=date(
        2016, 1, 1), end_date=date(2017, 1, 1))

    def test_current_memberships(self, derrida):
        """project should return its current team members"""
        # should return team from 2016-2017 grant plus old members who stayed on
        katie = Person.objects.get(first_name="Katie", last_name="Chenoweth")
        rsk = Person.objects.get(first_name="Rebecca", last_name="Koeser")
        rm = Person.objects.get(first_name="Rebecca", last_name="Munson")
        chloe = Person.objects.get(first_name="Chloe", last_name="Vettier")
        renee = Person.objects.get(first_name="Renee", last_name="Altergott")
        current_members = [m.person for m in derrida.current_memberships()]
        assert katie in current_members     # 2015-2017
        assert rsk in current_members       # 2015-2017
        assert rm not in current_members    # 2015-2016
        assert chloe in current_members     # 2016-2017
        assert renee in current_members     # 2016-2017

    def test_alums(self, derrida):
        """project should return past team members (alums)"""
        # should return only people who are not currently on project
        katie = Person.objects.get(first_name="Katie", last_name="Chenoweth")
        rsk = Person.objects.get(first_name="Rebecca", last_name="Koeser")
        rm = Person.objects.get(first_name="Rebecca", last_name="Munson")
        chloe = Person.objects.get(first_name="Chloe", last_name="Vettier")
        renee = Person.objects.get(first_name="Renee", last_name="Altergott")
        alums = [m.person for m in derrida.alums()]
        assert katie not in alums     # 2015-2017
        assert rsk not in alums       # 2015-2017
        assert rm in alums            # 2015-2016
        assert chloe not in alums     # 2016-2017
        assert renee not in alums     # 2016-2017
