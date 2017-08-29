from django.conf.urls import url

from cdhweb.projects import views


urlpatterns = [
    # url('^$', views.EventListView.as_view(), name='list'),
   # url('^(?P<year>\d{4})/$', views.EventListView.as_view(), name='year-list'),
    url(r'^(?P<slug>[\w-]+)/$', views.ProjectDetailView.as_view(), name='detail'),
]
