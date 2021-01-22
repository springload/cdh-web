from django.conf.urls import url

from cdhweb.projects import views

app_name = 'projects'
urlpatterns = [
    url('^$', views.SponsoredProjectListView.as_view(), name='list'),
    url('^staff/$', views.StaffProjectListView.as_view(), name='staff'),
    url('^working-groups/$', views.WorkingGroupListView.as_view(), name='working-groups'),
]
