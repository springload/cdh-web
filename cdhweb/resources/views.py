from random import shuffle

from django.shortcuts import render

from cdhweb.events.models import Event
from cdhweb.projects.models import Project


def site_index(request):
    '''Site home page.'''
    # TODO: highlighted/featured item or news

    # get highlighted, published projects
    # TODO: (maybe) published(for_user=request.user)
    projects = list(Project.objects.published().highlighted())
    # randomize the project list
    shuffle(projects)

    # find the next three upcoming, published events
    # TODO: (maybe) published(for_user=request.user) \
    upcoming_events = Event.objects.published() \
        .upcoming()[:3]

    return render(request, 'site_index.html', {
        'projects': projects[:4],   # first four of random list
        'events': upcoming_events
    })
