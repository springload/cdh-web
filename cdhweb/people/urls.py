from django.conf.urls import url
from django.views.generic.base import RedirectView

from cdhweb.people import views

app_name = 'people'
urlpatterns = [
    # for now, no generic people list page exists
    # url('^$', views.ProfileListView.as_view(), name='list'),
    url(r'^staff/$', views.StaffListView.as_view(), name='staff'),
    url(r'^postdocs/$', views.PostdocListView.as_view(), name='postdocs'),
    url(r'^students/$', views.StudentListView.as_view(), name='students'),
    url(r'^affiliates/$', views.AffiliateListView.as_view(), name='affiliates'),
    url(r'^speakers/$', views.SpeakerListView.as_view(), name='speakers'),
    url(r'^executive-committee/$', views.ExecListView.as_view(), name='exec-committee'),
    # redirect from /people/faculty -> /people/affiliates
    url(r'^faculty/$', RedirectView.as_view(url='/people/affiliates/', permanent=True)),
    url(r'^(?P<slug>[\w-]+)/$', views.ProfileDetailView.as_view(), name='profile'),
]