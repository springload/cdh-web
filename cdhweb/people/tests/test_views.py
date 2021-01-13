from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
import pytest
from pytest_django.asserts import assertContains, assertNotContains

# NOTE: person factory fixtures in conftest


@pytest.mark.django_db
class TestStaffListView:
    url = reverse('people:staff')

    def test_list_current(self, client, staffer, postdoc, student):
        '''test staff list view current members'''
        response = client.get(self.url)
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

        # check display
        # staff member should display and current title, but not years
        assertContains(response, staffer.first_name)
        prev_position = staffer.positions.last()
        assertNotContains(response, prev_position.title)
        assertContains(response, staffer.current_title)

        assertNotContains(response, prev_position.years)
        assertNotContains(response, staffer.positions.first().years)

        # postdoc info
        assertContains(response, postdoc.first_name)
        assertContains(response, postdoc.current_title)

    @pytest.mark.skip
    def test_profilepage_links(self, client, staffer, postdoc):
        '''test that profile page links are present'''
        response = client.get(self.url)
        # TODO: requires creating profile landing page & profile pages!
        assertContains(response, staffer.profilepage.url)
        assertContains(response, postdoc.profilepage.url)

    def test_future_end(self, client, staffer):
        '''test staff member with future end date'''
        # position with future end date should be current
        position = staffer.positions.first()
        position.end_date = timezone.now() + timedelta(days=30)
        position.save()
        response = client.get(self.url)
        # staffer should be current
        assert staffer in response.context['current']
        assert staffer not in response.context['past']

    def test_list_past(self, client, postdoc):
        '''test postdoc with position end date in the past'''
        position = postdoc.positions.last()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        response = client.get(self.url)
        # postdoc should be past
        assert postdoc in response.context['past']
        assert postdoc not in response.context['current']
        # should display years
        assertContains(response, postdoc.positions.first().years)


@pytest.mark.django_db
class TestStudentListView:
    url = reverse('people:students')

    def test_list_current(self, client, student, staffer, grad_pi):
        '''test current student'''
        response = client.get(self.url)
        # student assistant should be included
        assert student in response.context['current']
        # grad pi included
        assert grad_pi in response.context['current']

        # doesn't include staff
        assert staffer not in response.context['current']
        assert staffer not in response.context['past']

        # displays student position / role
        assertContains(response, student.first_name)
        assertContains(response, student.positions.first().title)
        assertContains(response, grad_pi.first_name)
        assertContains(response, grad_pi.membership_set.first().role.title)

    def test_student_list_past(self, client, student):
        '''test past student'''
        position = student.positions.first()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        response = client.get(self.url)
        # student should be included in past
        assert student in response.context['past']
        assert student not in response.context['current']
        assertContains(response, student.first_name)
        assertContains(response, student.positions.first().title)
        assertContains(response, student.positions.first().years)


@pytest.mark.django_db
class TestAffiliateListView:
    url = reverse('people:affiliates')

    def test_list(self, client, staffer, faculty_pi, staff_pi):
        '''test current affiliate'''
        response = client.get(self.url)
        assert faculty_pi in response.context['current']
        assert staff_pi in response.context['current']
        assert staffer not in response.context['current']

        # should display name and date from latest grant
        grant = faculty_pi.project_set.first().latest_grant()
        assertContains(response, '{}–{} {} Grant Recipient'.format(
            grant.start_date.year,
            grant.end_date.year,
            grant.grant_type.grant_type), html=True)

        grant = staff_pi.project_set.first().latest_grant()
        assertContains(response, '{}–{} {} Grant Recipient'.format(
            grant.start_date.year,
            grant.end_date.year,
            grant.grant_type.grant_type), html=True)


@pytest.mark.skip('todo')
@pytest.mark.django_db
class TestSpeakersListView:
    url = reverse('people:speakers')

    def test_list_current(self, client, speaker):
        '''test upcoming speakers'''
        response = client.get(self.url)
        assert speaker in response.context['current']
