from random import shuffle

from django.shortcuts import render

from cdhweb.events.models import Event
from cdhweb.projects.models import Project


def site_index(request):
    '''Site home page.'''
    # TODO: highlighted/featured item or news

    # get current, active, published projects
    projects = list(Project.objects.published(for_user=request.user) \
                                   .active().current())
    # randomize the project list
    shuffle(projects)

    # find the next three upcoming, published events
    upcoming_events = Event.objects.published(for_user=request.user) \
        .upcoming()[:3]

    return render(request, 'site_index.html', {
        'projects': projects[:4],   # first four of random list
        'events': upcoming_events
    })
