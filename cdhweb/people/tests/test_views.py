from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
import pytest
from pytest_django.asserts import assertContains, assertNotContains

from cdhweb.people.models import Person
from cdhweb.people.views import AffiliateListView, ExecListView, \
    StaffListView, StudentListView, PersonListView

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

    def test_display_label_current(self, staffer):
        '''test display label for current staff'''
        assert StaffListView().display_label(staffer) == \
            staffer.positions.first().title

    def test_display_label_past(self, postdoc):
        '''test display label for past staff'''
        position = postdoc.positions.last()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        assert StaffListView().display_label(postdoc) == \
            '%s %s' % (position.years, position.title)


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
        # should not display "project director" role
        assertNotContains(response, grad_pi.membership_set.first().role.title)
        assertContains(response,
                       '%s Grant Recipient' % grad_pi.latest_grant.grant_type)

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

    def test_display_label_current(self, student, grad_pi, grad_pm):
        '''test display label for current student'''
        assert StudentListView().display_label(student) == \
            str(student.positions.first().title)

        grant = grad_pi.latest_grant
        assert StudentListView().display_label(grad_pi) == \
            "%s %s Grant Recipient" % (grant.years, grant.grant_type)

        assert StudentListView().display_label(grad_pm) == 'Project Manager'

    def test_display_label_past(self, student, grad_pi, grad_pm):
        '''test display label for former student affiliates'''
        position = student.positions.last()
        position.end_date = timezone.now() - timedelta(days=30)
        position.save()
        assert StudentListView().display_label(student) == \
            '%s %s' % (position.years, position.title)

        grant = grad_pi.latest_grant
        grant.end_date = timezone.now() - timedelta(days=30)
        grant.save()
        assert StudentListView().display_label(grad_pi) == \
            "%s %s Grant Recipient" % (grant.years, grant.grant_type)

        membership = grad_pm.membership_set.first()
        membership.end_date = timezone.now() - timedelta(days=30)
        membership.save()
        assert StudentListView().display_label(grad_pm) == \
            '%s Project Manager' % membership.years


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

    def test_display_label(self, faculty_pi):
        '''test display label for current faculty/staff affiliate'''
        grant = faculty_pi.latest_grant
        assert AffiliateListView().display_label(faculty_pi) == \
            '%s %s Grant Recipient' % (grant.years, grant.grant_type)

        # switch to faculty fellowship to test custom display logic
        grant_type = grant.grant_type
        grant_type.grant_type = 'Faculty Fellowship'
        grant_type.save()
        assert AffiliateListView().display_label(faculty_pi) == \
            '%s Faculty Fellow' % grant.years


@pytest.mark.django_db
class TestExecListView:
    url = reverse('people:exec-committee')

    def test_list_current(self, client, faculty_exec, staff_exec):
        '''test current exec members'''
        response = client.get(self.url)
        assert faculty_exec in response.context['current']
        assert staff_exec in response.context['sits_with']

    def test_list_past(self, client, faculty_exec, staff_exec):
        '''test past exec members'''
        for position in [faculty_exec.positions.first(),
                         staff_exec.positions.first()]:
            position.end_date = timezone.now() - timedelta(days=30)
            position.save()

        response = client.get(self.url)
        assert faculty_exec in response.context['past']
        assert staff_exec in response.context['past']

    def test_display_label(self):
        '''test display label for exec'''
        exec_member = Person.objects.create(
            first_name='Laura', job_title='Professor of Humanities')
        assert ExecListView().display_label(exec_member) == \
            exec_member.job_title


@pytest.mark.django_db
def test_speakers_list_gone(client):
    response = client.get('/people/speakers/')
    assert response.status_code == 410
    assertContains(response, '410', status_code=410)
    assertContains(response, "That page isn&#39;t here anymore.",
                   status_code=410)
    assertNotContains(response, '404', status_code=410)
    assertNotContains(response, "can't seem to find", status_code=410)


@pytest.mark.django_db
def test_personlistview_displaylabel_notimplemented(grad_pm):
    # base person list view class display label raises not implemented
    with pytest.raises(NotImplementedError):
        PersonListView().display_label(grad_pm)
