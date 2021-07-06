from datetime import datetime, timedelta

import pytest
from cdhweb.people.models import Person
from cdhweb.projects.models import (
    Grant,
    GrantType,
    Membership,
    Project,
    ProjectsLandingPage,
    Role,
)


def add_project_member(project, role, start_date=None, end_date=None, **person_opts):
    """factory method to create a person and give them a role on a project"""
    role = Role.objects.get_or_create(title=role)[0]
    person = Person.objects.create(**person_opts)
    Membership.objects.create(
        project=project,
        role=role,
        person=person,
        start_date=start_date,
        end_date=end_date,
    )
    return person


def make_projects_landing_page(homepage):
    """create a test projects landing page underneath the homepage"""
    plp = ProjectsLandingPage(
        title="projects", slug="projects", tagline="let's do some stuff"
    )
    homepage.add_child(instance=plp)
    homepage.save()
    return plp


def make_derrida(projects_landing_page):
    """a sponsored project with two different grants and project teams"""
    # create the project
    derrida = Project(
        title="Derrida's Margins", short_description="derrida description"
    )
    projects_landing_page.add_child(instance=derrida)
    projects_landing_page.save()

    # dates used
    tomorrow = datetime.today() + timedelta(days=1)
    one_year_ago = datetime.today() - timedelta(days=365)
    two_years_ago = one_year_ago - timedelta(days=365)

    # add grants: DCG from last year and RPG from this year
    dcg = GrantType.objects.get_or_create(grant_type="Dataset Curation")[0]
    rpg = GrantType.objects.get_or_create(grant_type="Research Partnership")[0]
    Grant.objects.create(
        project=derrida, grant_type=dcg, start_date=two_years_ago, end_date=one_year_ago
    )
    Grant.objects.create(
        project=derrida, grant_type=rpg, start_date=one_year_ago, end_date=tomorrow
    )

    # add memberships for initial project team (first year)
    add_project_member(
        derrida,
        "Project Director",
        start_date=two_years_ago,
        end_date=tomorrow,
        first_name="Katie",
        last_name="Chenoweth",
    )
    add_project_member(
        derrida,
        "Lead Developer",
        start_date=two_years_ago,
        end_date=tomorrow,
        first_name="Rebecca",
        last_name="Koeser",
    )
    add_project_member(
        derrida,
        "Project Manager",
        start_date=two_years_ago,
        end_date=one_year_ago,
        first_name="Rebecca",
        last_name="Munson",
    )

    # add new memberships for past year
    add_project_member(
        derrida,
        "Grad Assistant",
        start_date=one_year_ago,
        end_date=tomorrow,
        first_name="Chloe",
        last_name="Vettier",
    )
    add_project_member(
        derrida,
        "Project Manager",
        start_date=one_year_ago,
        end_date=tomorrow,
        first_name="Renee",
        last_name="Altergott",
    )

    return derrida


def make_pliny(projects_landing_page):
    """a staff r&d project with one current r&d grant and one current member"""
    # create the project
    pliny = Project(title="Pliny Project", short_description="pliny description")
    projects_landing_page.add_child(instance=pliny)
    projects_landing_page.save()

    # add a staff r&d grant and one member; no end date so grant/role is current
    start_date = datetime.today() - timedelta(days=400)
    srd = GrantType.objects.get_or_create(grant_type="Staff R&D")[0]
    Grant.objects.create(project=pliny, grant_type=srd, start_date=start_date)
    add_project_member(
        pliny,
        "Project Director",
        start_date=start_date,
        first_name="Ben",
        last_name="Hicks",
    )

    return pliny


def make_ocampo(projects_landing_page):
    """a postdoctoral research project with one r&d grant and one current member"""
    # create the project
    ocampo = Project(
        title="Global Networks of Cultural Production",
        short_description="ocampo description",
    )
    projects_landing_page.add_child(instance=ocampo)
    projects_landing_page.save()

    # add a postdoc grant and one member; no end date so grant/role is current
    start_date = datetime.today() - timedelta(days=450)
    prp = GrantType.objects.get_or_create(grant_type="Postdoctoral Research Project")[0]
    Grant.objects.create(project=ocampo, grant_type=prp, start_date=start_date)
    add_project_member(
        ocampo,
        "Project Director",
        start_date=start_date,
        first_name="Nora",
        last_name="Benedict",
    )

    return ocampo


def make_slavic(projects_landing_page):
    """a dh working group with one expired seed grant and one current member"""
    # create the working group
    slavic = Project(
        title="Slavic DH Working Group",
        short_description="slavic description",
        working_group=True,
    )
    projects_landing_page.add_child(instance=slavic)
    projects_landing_page.save()

    # dates used
    one_year_ago = datetime.today() - timedelta(days=365)
    two_years_ago = one_year_ago - timedelta(days=365)

    # add a seed grant and one member; grant ended but membership is current
    seed = GrantType.objects.get_or_create(grant_type="Seed")[0]
    Grant.objects.create(
        project=slavic, grant_type=seed, start_date=two_years_ago, end_date=one_year_ago
    )
    add_project_member(
        slavic,
        "Chair",
        start_date=two_years_ago,
        first_name="Natalia",
        last_name="Ermolaev",
    )

    return slavic


def make_projects(projects_landing_page):
    """convience function to create several projects and associated models"""
    return {
        "derrida": make_derrida(projects_landing_page),
        "pliny": make_pliny(projects_landing_page),
        "ocampo": make_ocampo(projects_landing_page),
        "slavic": make_slavic(projects_landing_page),
    }


@pytest.fixture
def projects_landing_page(db, homepage):
    return make_projects_landing_page(homepage)


@pytest.fixture
def derrida(db, projects_landing_page):
    return make_derrida(projects_landing_page)


@pytest.fixture
def pliny(db, projects_landing_page):
    return make_pliny(projects_landing_page)


@pytest.fixture
def ocampo(db, projects_landing_page):
    return make_ocampo(projects_landing_page)


@pytest.fixture
def slavic(db, projects_landing_page):
    return make_slavic(projects_landing_page)


@pytest.fixture
def projects(db, projects_landing_page):
    return make_projects(projects_landing_page)
