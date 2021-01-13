from datetime import date

import pytest

from cdhweb.people.models import Person, Position, Title


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
    developer = Title.objects.get(title='DH Developer')
    # give the staffer a second position
    Position.objects.create(person=staff_person, title=developer,
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
