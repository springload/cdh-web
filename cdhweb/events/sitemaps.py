from django.contrib.sitemaps import Sitemap
from django.test import RequestFactory
from django.urls import reverse

from cdhweb.events import views


class EventViewsSitemap(Sitemap):
    '''Sitemap for project views that are neither Wagtail pages nor
    tied to models (currently event upcoming and semester list views).'''

    def items(self):
        # return list of tuple with url, initialized view object
        factory = RequestFactory()

        urls = [
            (reverse('event:upcoming'), views.UpcomingEventsView()),
        ]
        # get list of actual semesters with events
        for season, year in views.EventSemesterDates() \
                                 .get_semester_date_list():
            # generate url for this date,
            # and initialize a view for that url so we can get last modified
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
        # return the url as generated in items method
        return obj[0]

    def lastmod(self, obj):
        # return last modified as calculated by the view
        return obj[1].last_modified()
