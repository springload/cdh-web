from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

# NOTE: person factory fixtures in conftest


@pytest.mark.django_db
class TestStaffListView:

    def test_list_current(self, client, staffer, postdoc, student):
        '''test staff list view current members'''
        response = client.get(reverse('people:staff'))
        # staffer should be included
        assert staffer in response.context['current']
        # postdoc also
        assert postdoc in response.context['current']
        # no duplicates even with multiple positions
        assert len(response.context['current']) == 2
        # past staff list is empty
        assert not response.context['past']
        # doesn't include students
        assert student not in response.context['current']
        assert student not in response.context['past']

    def test_future_end(self, client, staffer):
        '''test staff member with future end date'''
        # position with future end date should be current
        position = staffer.positions.first()
        position.end_date = timezone.now() + timedelta(days=30)
        position.save()
        response = client.get(reverse('people:staff'))
        # staffer should be current
        assert staffer in response.context['current']
        assert staffer not in response.context['past']

    def test_list_past(self, client, postdoc):
        '''test postdoc with position end date in the past'''
        position = postdoc.positions.last()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        response = client.get(reverse('people:staff'))
        # postdoc should be past
        assert postdoc in response.context['past']
        assert postdoc not in response.context['current']


@pytest.mark.django_db
class TestStudentListView:

    def test_list_current(self, client, student, staffer):
        '''test current student'''
        response = client.get(reverse('people:students'))
        # student should be included
        assert student in response.context['current']
        assert student not in response.context['past']
        # doesn't include staff
        assert staffer not in response.context['current']
        assert staffer not in response.context['past']

    def test_student_list_past(self, client, student):
        '''test past student'''
        position = student.positions.first()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        response = client.get(reverse('people:students'))
        # student should be included in past
        assert student in response.context['past']
        assert student not in response.context['current']
