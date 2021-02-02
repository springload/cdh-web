from django.conf.urls import url
from django.views.generic.base import RedirectView

from cdhweb.people import views

app_name = 'people'
urlpatterns = [
    # for now, no generic people list page exists
    # url('^$', views.ProfileListView.as_view(), name='list'),
    url(r'^staff/$', views.StaffListView.as_view(), name='staff'),
    url(r'^students/$', views.StudentListView.as_view(), name='students'),
    url(r'^affiliates/$', views.AffiliateListView.as_view(), name='affiliates'),
    url(r'^executive-committee/$', views.ExecListView.as_view(), name='exec-committee'),
    # redirect from /people/faculty -> /people/affiliates
    url(r'^faculty/$', RedirectView.as_view(url='/people/affiliates/', permanent=True)),
    # redirect from /people/postdocs -> /people/staff
    url(r'^postdocs/$', RedirectView.as_view(url='/people/staff/', permanent=True)),
    # return 410 gone for speakers list view; unnamed to prevent links
    # (removed in 3.0, no longer needed post Year of Data)
    url(r'^speakers/$', RedirectView.as_view(url=None)),

]