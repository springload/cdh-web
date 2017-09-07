from django.conf.urls import url

from . import views


urlpatterns = [
    url('^$', views.BlogIndexView.as_view(), name='list'),
    url('^(?P<year>\d{4})/$', views.BlogYearArchiveView.as_view(),
        name='by-year'),
    url("^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)/$",
        views.BlogDetailView.as_view(), name='detail'),
]
