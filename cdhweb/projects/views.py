from django.shortcuts import render
from django.views.generic.detail import DetailView

from cdhweb.projects.models import Project


class ProjectDetailView(DetailView):
    model = Project

    def get_queryset(self):
        return Project.objects.published(for_user=self.request.user)
