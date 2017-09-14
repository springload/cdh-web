from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Profile


class ProfileMixinView(object):
    '''Profile view mixin that sets model to Profile and returns a
    published Profile queryset.'''

    model = Profile

    def get_queryset(self):
        # use displayable manager to find published profiles only
        # (or draft profiles for logged in users with permission to view)
        return Profile.objects.published() # TODO: published(for_user=self.request.user)



class ProfileDetailView(ProfileMixinView, DetailView):
    pass


class ProfileListView(ProfileMixinView, ListView):
    # NOTE: we probably don't need a full list of all profiles;
    # instead we'll probably want a few filtered lists, e.g. current
    # staff, guest speakers, alumni, etc.
    pass

class StaffListView(ProfileMixinView, ListView):

    def get_queryset(self):
        return super(StaffListView, self).get_queryset().filter(is_staff=True)

    def get_context_data(self):
        context = super(StaffListView, self).get_context_data()
        context.update({
            'title': 'Who we are'
        })
        return context



