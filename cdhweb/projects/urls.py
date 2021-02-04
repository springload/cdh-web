from django.urls import path

from cdhweb.projects import views

app_name = "projects"
urlpatterns = [
    path("", views.SponsoredProjectListView.as_view(), name="sponsored"),
    path("staff/", views.StaffProjectListView.as_view(), name="staff"),
    path("working-groups", views.WorkingGroupListView.as_view(), name="working-groups"),
]
