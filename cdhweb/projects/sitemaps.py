from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from cdhweb.projects import views


class ProjectViewsSitemap(Sitemap):
    '''Sitemap for project views that are neither Wagtail pages nor
    tied to models (currently all project list views).'''

    def items(self):
        # return list of tuple with url name, view object
        return [
            ('sponsored', views.SponsoredProjectListView),
            ('staff', views.StaffProjectListView),
            ('working-groups', views.WorkingGroupListView),
        ]

    def location(self, obj):
        # generate url based on archives url names
        return reverse('projects:%s' % obj[0])

    def lastmod(self, obj):
        # both pages are modified based on changes to digitized works,
        # so return the most recent modification time of any of them
        return obj[1]().last_modified()
