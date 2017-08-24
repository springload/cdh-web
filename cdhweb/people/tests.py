from unittest.mock import Mock

from django.test import TestCase
from django.utils.text import slugify
import pytest

from .models import Title, Person, Position, init_profile_from_ldap


@pytest.mark.django_db
class TestTitle(TestCase):
    fixtures = ['test_people_data.json']

    def test_num_people(self):
        # test counts against fixture data
        faculty_director = Title.objects.filter(title='Faculty Director').first()
        assert faculty_director.num_people() == 0
        lead_developer = Title.objects.filter(title='Lead Developer').first()
        assert lead_developer.num_people() == 1


@pytest.mark.django_db
class TestPerson(TestCase):

    def test_current_title(self):
        # create test person and add two positions
        staffer = Person.objects.create(username='staff')
        staff_title = Title.objects.create(title='staff')
        fellow = Title.objects.create(title='fellow')
        Position.objects.create(user=staffer, title=fellow,
            start_date='2015-01-01', end_date='2015-12-31')
        Position.objects.create(user=staffer, title=staff_title,
            start_date='2016-06-01')
        assert staffer.current_title == staff_title


@pytest.mark.django_db
def test_init_profile_from_ldap():
    # create user to test with
    staffer = Person.objects.create(username='staff',
        email='STAFF@EXAMPLE.com')

    # use Mock to simulate ldap data provided by pucas
    ldapinfo = Mock(displayName='Joe E. Schmoe',
        # no telephone or office set
        telephoneNumber=[], street=[],
        title='Freeloader, World at large') # job title, organizational unit

    init_profile_from_ldap(staffer, ldapinfo)
    updated_staffer = Person.objects.get(username='staff')
    # email should be converted to lower case
    assert updated_staffer.email == staffer.email.lower()
    # profile should have been created
    assert updated_staffer.profile
    profile = updated_staffer.profile
    # profile fields should be autopopulated where content exists
    assert profile.title == ldapinfo.displayName
    assert profile.slug == slugify(ldapinfo.displayName)
    assert profile.phone_number == ''
    assert profile.office_location == ''
    # title should be created
    assert Title.objects.filter(title='Freeloader').exists()

    # ldap info with telephone and street
    ldapinfo.telephoneNumber = '4800'
    ldapinfo.street = '801B'
    init_profile_from_ldap(staffer, ldapinfo)
    profile = Person.objects.get(username='staff').profile
    assert profile.phone_number == ldapinfo.telephoneNumber
    assert profile.office_location == ldapinfo.street
    # title should not be duplicated
    assert Title.objects.filter(title='Freeloader').count() == 1

