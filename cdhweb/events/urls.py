from django.urls import path, re_path

from cdhweb.events import views

app_name = "events"
urlpatterns = [
    path("", views.EventsLandingPageView.as_view(), name="upcoming"),
    re_path(
        r"^(?P<semester>(fall|spring|summer))-(?P<year>\d{4})/$",
        views.EventsLandingPageView.as_view(),
        name="by-semester",
    ),
]
