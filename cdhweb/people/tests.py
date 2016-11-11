from django.test import TestCase
import pytest

from .models import Title, Person, Position


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

