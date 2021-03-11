from django.urls import path
from django.views.generic.base import RedirectView

from cdhweb.people import views

app_name = "people"
urlpatterns = [
    path("staff/", views.StaffListView.as_view(), name="staff"),
    path("students/", views.StudentListView.as_view(), name="students"),
    path("affiliates/", views.AffiliateListView.as_view(), name="affiliates"),
    path("executive-committee/", views.ExecListView.as_view(), name="exec-committee"),
    # speakers list was deleted; serve 410 gone
    path("speakers/", views.speakerlist_gone),
    # redirect from /people/faculty -> /people/affiliates
    path("faculty/", RedirectView.as_view(url="/people/affiliates/", permanent=True)),
    # redirect from /people/postdocs -> /people/staff
    path("postdocs/", RedirectView.as_view(url="/people/staff/", permanent=True)),
]
