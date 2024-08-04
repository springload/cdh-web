from django.urls import path

from cdhweb.people import views

app_name = "people"
urlpatterns = [
    # speakers list was deleted; serve 410 gone
    path("speakers/", views.speakerlist_gone),
]
