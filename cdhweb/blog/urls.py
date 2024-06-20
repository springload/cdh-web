from django.urls import path, re_path

from . import views

app_name = "blog"
urlpatterns = [
    re_path(r"^(?P<slug>[\w-]+)/$", views.BlogLandingPageView.as_view(), name="list"),
    re_path(
        r"^(?P<slug>[\w-]+)/(?P<year>\d{4})/$",
        views.BlogLandingPageView.as_view(),
        name="by-year",
    ),
    re_path(
        r"^(?P<slug>[\w-]+)/(?P<year>\d{4})/(?P<month>\d{2})/$",
        views.BlogLandingPageView.as_view(),
        name="by-month",
    ),
    path("rss/", views.RssBlogPostFeed(), name="rss"),
    path("atom/", views.AtomBlogPostFeed(), name="atom"),
]
