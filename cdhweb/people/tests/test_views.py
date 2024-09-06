from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains

from cdhweb.people.models import Person
from cdhweb.people.views import (
    AffiliateListView,
    ExecListView,
    PersonListView,
    StaffListView,
    StudentListView,
)

# NOTE: person factory fixtures in conftest


@pytest.mark.django_db
def test_speakers_list_gone(client):
    response = client.get("/people/speakers/")
    assert response.status_code == 410
    assertContains(response, "410", status_code=410)
    assertContains(response, "That page isn&#x27;t here anymore.", status_code=410)
    assertNotContains(response, "404", status_code=410)
    assertNotContains(response, "can't seem to find", status_code=410)


@pytest.mark.django_db
def test_personlistview_displaylabel_notimplemented(grad_pm):
    # base person list view class display label raises not implemented
    with pytest.raises(NotImplementedError):
        PersonListView().display_label(grad_pm)
