from datetime import timedelta
from operator import attrgetter
from unittest.mock import patch

from django.http import HttpResponse


class TestLastModifiedMixin:
    @patch("django.views.generic.detail.DetailView.dispatch")
    def test_last_modified(self, mock_dispatch, rf, lmod_view):
        """should send last modified date with response"""
        lmod = lmod_view.get_object().updated.replace(microsecond=0)
        # create a fake HttpResponse and check that header is set
        mock_dispatch.return_value = HttpResponse()
        response = lmod_view.dispatch(rf.get(""))
        assert response["Last-Modified"] == lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")

    @patch("django.views.generic.detail.DetailView.dispatch")
    def test_not_modified(self, mock_dispatch, rf, lmod_view):
        """should serve 304 if event has not been modified"""
        # request after current last mod date; should report unchanged
        lmod = lmod_view.get_object().updated + timedelta(seconds=1)
        request = rf.get(
            "", HTTP_IF_MODIFIED_SINCE=lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
        )
        mock_dispatch.return_value = HttpResponse()
        response = lmod_view.dispatch(request)
        assert response.status_code == 304

    @patch("django.views.generic.detail.DetailView.dispatch")
    def test_modified(self, mock_dispatch, rf, lmod_view):
        """should serve actual object via 200 if it has been modified"""
        # request using a date 1 day before most recent modification
        lmod = lmod_view.get_object().updated - timedelta(days=1)
        request = rf.get(
            "", HTTP_IF_MODIFIED_SINCE=lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
        )
        mock_dispatch.return_value = HttpResponse()
        response = lmod_view.dispatch(request)
        assert response.status_code == 200


class TestLastModifiedListMixin:
    @patch("django.views.generic.list.ListView.dispatch")
    def test_last_modified(self, mock_dispatch, rf, lmod_list_view, lmod_objects):
        """should send most recent modified date with response"""
        # get last modified date for most recent object
        most_recent = list(
            sorted(lmod_objects, key=attrgetter("updated"), reverse=True)
        )[0]
        lmod = most_recent.updated.replace(microsecond=0)
        # create a fake HttpResponse and check that header is most recent date
        mock_dispatch.return_value = HttpResponse()
        response = lmod_list_view.dispatch(rf.get(""))
        assert response["Last-Modified"] == lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")

    @patch("django.views.generic.list.ListView.dispatch")
    def test_not_modified(self, mock_dispatch, rf, lmod_list_view, lmod_objects):
        """should serve 304 if no objects have been modified since request"""
        # get last modified date for most recent object
        most_recent = list(
            sorted(lmod_objects, key=attrgetter("updated"), reverse=True)
        )[0]
        lmod = most_recent.updated + timedelta(seconds=1)
        request = rf.get(
            "", HTTP_IF_MODIFIED_SINCE=lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
        )
        # send it with request; nothing has been modified since then so 304
        mock_dispatch.return_value = HttpResponse()
        response = lmod_list_view.dispatch(request)
        assert response.status_code == 304

    @patch("django.views.generic.list.ListView.dispatch")
    def test_modified(self, mock_dispatch, rf, lmod_list_view, lmod_objects):
        """should serve full object list with 200 if any modified since request"""
        # get last modified date for most recent object
        most_recent = list(
            sorted(lmod_objects, key=attrgetter("updated"), reverse=True)
        )[0]
        lmod = most_recent.updated - timedelta(days=1)
        # request with prior date; should report modified since then
        request = rf.get(
            "", HTTP_IF_MODIFIED_SINCE=lmod.strftime("%a, %d %b %Y %H:%M:%S GMT")
        )
        mock_dispatch.return_value = HttpResponse()
        response = lmod_list_view.dispatch(request)
        assert response.status_code == 200
