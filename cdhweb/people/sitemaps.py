from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from cdhweb.people import views


class PeopleListSitemap(Sitemap):
    '''Sitemap for people views that are not Wagtail pages but also
    not tied to models (currently all people list views).'''

    def items(self):
        # return list of tuple with url name, view object
        return [
            ('staff', views.StaffListView),
            ('students', views.StudentListView),
            ('affiliates', views.AffiliateListView),
            ('exec-committee', views.ExecListView)
        ]

    def location(self, obj):
        # generate url based on url name within people url namespace
        return reverse('people:%s' % obj[0])

    def lastmod(self, obj):
        # return last modified as calculated by the view
        return obj[1]().last_modified()
