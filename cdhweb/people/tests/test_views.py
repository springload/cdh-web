from datetime import date, timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from cdhweb.people.models import Person, Position, Title


@pytest.fixture
def staffer():
    # fixture to create a staff person with staff position
    developer = Title.objects.get_or_create(title='DH Developer')[0]
    staff_person = Person.objects.create(first_name='Staffer', cdh_staff=True,
                                         pu_status='stf')
    # give the staffer two positions
    Position.objects.create(person=staff_person, title=developer,
                            start_date=date(2016, 3, 1), end_date=date(2018, 3, 1))
    Position.objects.create(person=staff_person, title=developer, start_date=date(2018, 3, 2))
    return staff_person


@pytest.fixture
@pytest.mark.django_db
def postdoc():
    # fixture to create a postdoc person
    postdoc_title = Title.objects.get_or_create(title='Postdoctoral Fellow')[0]
    postdoc_person = Person.objects.create(
        first_name='Postdoc', cdh_staff=True, pu_status='stf')
    Position.objects.create(
        person=postdoc_person, title=postdoc_title, start_date=date(2018, 3, 1))
    return postdoc_person


@pytest.mark.django_db
def test_staff_list_current(client, staffer, postdoc):
    response = client.get(reverse('people:staff'))
    # staffer should be included
    assert staffer in response.context['current']
    # postdoc also
    assert postdoc in response.context['current']
    # no duplicates even with multiple positions
    assert len(response.context['current']) == 2
    # past staff list is empty
    assert not response.context['past']


@pytest.mark.django_db
def test_staff_list_future_end(client, staffer):
    # position with future end date should be current
    position = staffer.positions.first()
    position.end_date = timezone.now() + timedelta(days=30)
    position.save()
    response = client.get(reverse('people:staff'))
    # staffer should be current
    assert staffer in response.context['current']
    assert staffer not in response.context['past']


@pytest.mark.django_db
def test_staff_list_past(client, postdoc):
    # set an end date in the past
    position = postdoc.positions.last()
    position.end_date = timezone.now() - timedelta(days=30)
    position.save()
    response = client.get(reverse('people:staff'))
    # postdoc should be past
    assert postdoc in response.context['past']
    assert postdoc not in response.context['current']
