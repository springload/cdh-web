from django.contrib.sitemaps import Sitemap
from django.test import RequestFactory
from django.urls import reverse

from cdhweb.events import views


class EventViewsSitemap(Sitemap):
    '''Sitemap for project views that are neither Wagtail pages nor
    tied to models (currently all list views).'''

    def items(self):
        # return list of tuple with url name, view object
        factory = RequestFactory()

        urls = [
            (reverse('event:upcoming'), views.UpcomingEventsView()),
        ]
        for season, year in views.EventSemesterDates() \
                                 .get_semester_date_list():

            url = reverse('event:by-semester',
                          kwargs={'semester': season.lower(), 'year': year})
            request = factory.get(url)
            view = views.EventSemesterArchiveView()
            view.setup(request)
            urls.append((
                url, view
            ))
        return urls

    def location(self, obj):
        return obj[0]

    def lastmod(self, obj):
        # both pages are modified based on changes to digitized works,
        # so return the most recent modification time of any of them
        return obj[1].last_modified()
