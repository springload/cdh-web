from random import shuffle

from django.views.generic.base import TemplateView

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event
from cdhweb.projects.models import Project


class Homepage(TemplateView):
    '''Site home page.'''
    template_name = 'site_index.html'

    def get_context_data(self, *args, **kwargs):
        # use up to 6 featured posts if there are any
        updates = BlogPost.objects.featured().live().recent()[:6]
        if not updates.exists():
            # otherwise use 3 most recent posts
            updates = BlogPost.objects.live().recent()[:3]

        # get highlighted, published projects
        # TODO: (maybe) published(for_user=request.user)
        projects = list(Project.objects.live().highlighted())
        # randomize the project list
        shuffle(projects)

        # find the next three upcoming, published events
        # TODO: (maybe) published(for_user=request.user) \
        upcoming_events = Event.objects.live().upcoming()[:3]

        return {
            'updates': updates,
            'projects': projects[:4],   # first four of random list
            'events': upcoming_events
        }
