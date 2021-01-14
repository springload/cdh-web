from datetime import date, timedelta

import pytest

from cdhweb.people.models import Person, Position, Title
from cdhweb.projects.models import Grant, GrantType, Project, Role, Membership


def create_person_with_position(position, start_date=None, end_date=None,
                                **person_opts):
    '''factory method to create person with position for fixtures'''
    position = Title.objects.get_or_create(title=position)[0]
    person = Person.objects.create(**person_opts)
    Position.objects.create(person=person, title=position,
                            start_date=start_date, end_date=end_date)
    return person


@pytest.fixture
def staffer():
    '''fixture to create a staff person with two staff positions'''
    staff_person = create_person_with_position(
        'DH Developer',
        start_date=date(2016, 3, 1), end_date=date(2018, 3, 1),
        first_name='Staffer', cdh_staff=True, pu_status='stf')
    rse = Title.objects.get_or_create(title='Research Sofware Engineer')[0]
    # give the staffer a second position
    Position.objects.create(person=staff_person, title=rse,
                            start_date=date(2018, 3, 2))
    return staff_person


@pytest.fixture
def postdoc():
    '''fixture to create a postdoc person'''
    return create_person_with_position(
        'Postdoctoral Fellow',
        start_date=date(2018, 3, 1),
        first_name='Postdoc', cdh_staff=True, pu_status='stf')


@pytest.fixture
def student():
    '''fixture to create a student person record'''
    return create_person_with_position(
        'Undergraduate Assistant',
        start_date=date(2018, 3, 1),
        first_name='student', cdh_staff=True, pu_status='undergraduate')


@pytest.fixture
def grad_pi():
    person = Person.objects.create(
        first_name='Tom', cdh_staff=False, pu_status='graduate')
    project = Project.objects.create(title='Chinese Exchange Poems')
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2015, 9, 1))
    return person


@pytest.fixture
def faculty_pi():
    person = Person.objects.create(
        first_name='Josh', cdh_staff=False, pu_status='fac')
    project = Project.objects.create(title='MEP')
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    dataset_curation = GrantType.objects.get_or_create(grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2019, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2016, 9, 1))
    return person


@pytest.fixture
def staff_pi():
    person = Person.objects.create(
        first_name='Thomas', cdh_staff=False, pu_status='stf')
    project = Project.objects.create(title='SVP')
    project_director = Role.objects.get_or_create(title='Project Director')[0]
    dataset_curation = GrantType.objects.get_or_create(grant_type='Dataset Curation')[0]
    Grant.objects.create(grant_type=dataset_curation, project=project,
                         start_date=date(2020, 9, 1),
                         end_date=date.today() + timedelta(days=30))
    Membership.objects.create(
        project=project, person=person, role=project_director,
        start_date=date(2016, 9, 1))
    return person


@pytest.fixture
def faculty_exec():
    return create_person_with_position(
        'Executive Committee Member',
        start_date=date(2018, 3, 1),
        first_name='Anna', cdh_staff=False, pu_status='fac')


@pytest.fixture
def staff_exec():
    return create_person_with_position(
        'Sits with Executive Committee',
        start_date=date(2010, 3, 1),
        first_name='Jay', cdh_staff=False, pu_status='stf')
