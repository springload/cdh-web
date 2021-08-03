from django.urls import path, re_path

from . import views

app_name = "blog"
urlpatterns = [
    path("", views.BlogIndexView.as_view(), name="list"),
    re_path(r"^(?P<year>\d{4})/$", views.BlogYearArchiveView.as_view(), name="by-year"),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/$",
        views.BlogMonthArchiveView.as_view(),
        name="by-month",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$",
        views.BlogDetailView.as_view(),
        name="detail",
    ),
    path("rss/", views.RssBlogPostFeed(), name="rss"),
    path("atom/", views.AtomBlogPostFeed(), name="atom"),
]
