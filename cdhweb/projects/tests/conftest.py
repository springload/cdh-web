import pytest
from datetime import date
from cdhweb.pages.models import HomePage
from cdhweb.people.models import Person
from cdhweb.projects.models import Membership, ProjectsLandingPage, Role, Project, Grant, GrantType
from wagtail.core.models import Page, Site


def add_project_member(project, role, start_date=None, end_date=None, **person_opts):
    """factory method to create a person and give them a role on a project"""
    role = Role.objects.get_or_create(title=role)[0]
    person = Person.objects.create(**person_opts)
    Membership.objects.create(project=project, role=role,
                              person=person, start_date=start_date, end_date=end_date)
    return person


@pytest.fixture
def projects_landing_page(db, homepage):
    """create a test projects landing page underneath the homepage"""
    landing = ProjectsLandingPage(
        title="projects", slug="projects", tagline="cdh projects")
    homepage.add_child(instance=landing)
    homepage.save()
    return landing


@pytest.fixture
def derrida(db, projects_landing_page):
    """create and return a project with two different grants/project teams"""
    # create the project
    derrida = Project(title="Derrida's Margins")
    projects_landing_page.add_child(instance=derrida)
    projects_landing_page.save()

    # add grants: 2015-2016 DCG and 2016-2017 RPG
    dcg = GrantType.objects.get_or_create(grant_type="Dataset Curation")[0]
    rpg = GrantType.objects.get_or_create(grant_type="Research Partnership")[0]
    Grant.objects.create(project=derrida, grant_type=dcg, start_date=date(
        2015, 1, 1), end_date=date(2016, 1, 1))
    Grant.objects.create(project=derrida, grant_type=rpg, start_date=date(
        2016, 1, 1), end_date=date(2017, 1, 1))

    # add memberships for initial project team
    add_project_member(derrida, "Project Director", start_date=date(
        2015, 1, 1), end_date=date(2017, 1, 1), first_name="Katie", last_name="Chenoweth")
    add_project_member(derrida, "Lead Developer", start_date=date(
        2015, 1, 1), end_date=date(2017, 1, 1), first_name="Rebecca", last_name="Koeser")
    add_project_member(derrida, "Project Manager", start_date=date(
        2015, 1, 1), end_date=date(2016, 1, 1), first_name="Rebecca", last_name="Munson")

    # add new memberships for 2016-2017 year
    add_project_member(derrida, "Grad Assistant", start_date=date(
        2016, 1, 1), end_date=date(2017, 1, 1), first_name="Chloe", last_name="Vettier")
    add_project_member(derrida, "Project Manager", start_date=date(
        2016, 1, 1), end_date=date(2017, 1, 1), first_name="Renee", last_name="Altergott")

    return derrida
