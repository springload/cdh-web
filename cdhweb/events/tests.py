from django.test import TestCase

from datetime import datetime
from .models import Event


class TestEvent(TestCase):

    def test_get_absolute_url(self):
        jan15 = datetime(2015, 1, 15)
        evt = Event(start_time=jan15, end_time=jan15,
            slug='some-workshop')
        # single-digit months should be converted to two-digit for url
        assert '/events/2015/01/some-workshop/' == evt.get_absolute_url()
