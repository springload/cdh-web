from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains

from cdhweb.people.models import Person

# NOTE: person factory fixtures in conftest


@pytest.mark.django_db
def test_speakers_list_gone(client):
    response = client.get("/people/speakers/")
    assert response.status_code == 410


@pytest.mark.skip("no longer any 410 template?")
@pytest.mark.django_db
def test_speakers_list_gone(client):
    response = client.get("/people/speakers/")
    assertContains(response, "410", status_code=410)
    assertContains(response, "That page isn&#x27;t here anymore.", status_code=410)
    assertNotContains(response, "404", status_code=410)
    assertNotContains(response, "can't seem to find", status_code=410)
