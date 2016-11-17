from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.ProfileListView.as_view(), name='list'),
    url('^(?P<slug>[\w-]+)/$', views.ProfileDetailView.as_view(), name='profile'),
]