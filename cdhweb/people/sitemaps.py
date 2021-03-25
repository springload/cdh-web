from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from cdhweb.people import views


class PeopleViewsSitemap(Sitemap):
    '''Sitemap for people views that are not Wagtail pages but also
    not tied to models (currently archive search/browse page only).'''

    def items(self):
        # return list of tuple with url name, view object
        return [
            ('staff', views.StaffListView),
            ('students', views.StudentListView),
            ('affiliates', views.AffiliateListView),
            ('exec-committee', views.ExecListView)
        ]

    def location(self, obj):
        # generate url based on archives url names
        return reverse('people:%s' % obj[0])

    def lastmod(self, obj):
        # both pages are modified based on changes to digitized works,
        # so return the most recent modification time of any of them
        return obj[1]().last_modified()
