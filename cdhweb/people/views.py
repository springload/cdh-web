from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Profile


class ProfileDetailView(DetailView):
    model = Profile

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)


class ProfileListView(ListView):
    model = Profile

    # NOTE: we probably don't need a full list of all profiles;
    # instead we'll probably want a few filtered lists, e.g. current
    # staff, guest speakers, alumni, etc.

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)




