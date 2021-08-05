from django.urls import path, re_path

from cdhweb.events import views

app_name = "events"
urlpatterns = [
    path("", views.UpcomingEventsView.as_view(), name="upcoming"),
    re_path(
        r"^(?P<semester>(fall|spring|summer))-(?P<year>\d{4})/$",
        views.EventSemesterArchiveView.as_view(),
        name="by-semester",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+)/$",
        views.EventDetailView.as_view(),
        name="detail",
    ),
    re_path(
        r"^(?P<year>\d{4})/(?P<month>\d{2})/(?P<slug>[\w-]+).ics$",
        views.EventIcalView.as_view(),
        name="ical",
    ),
]
