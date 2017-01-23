from django.shortcuts import render

from cdhweb.events.models import Event
from cdhweb.projects.models import Project

def site_index(request):
    '''Site home page.'''
    # TODO: highlighted/featured item or news

    projects = Project.objects.published(for_user=request.user) \
        .active()
        # NOTE: temporarily suppress current filter
        # (requires project / grant association)
        # .current()

    # NOTE: could potentially also filter by type of grant ?
    # TODO: shuffle and pick first 3
    # (shouldn't be so many current, active projects that this is a problem)

    # find the next three upcoming, published events
    upcoming_events = Event.objects.published(for_user=request.user) \
        .upcoming()[:3]

    return render(request, 'site_index.html',
        {'projects': projects, 'events': upcoming_events})
