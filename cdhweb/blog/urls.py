from django.urls import path, re_path

from . import views

app_name = "blog"
urlpatterns = [
    path("rss/", views.RssBlogPostFeed(), name="rss"),
    path("atom/", views.AtomBlogPostFeed(), name="atom"),
]
