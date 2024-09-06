from django import forms
from django.db import models
from wagtail.models import Page

from cdhweb.blog.models import BlogPost
from cdhweb.events.models import Event
from cdhweb.people.models import Profile
from cdhweb.projects.models import Project


class SiteSearchFilters(models.TextChoices):
    EVERYTHING = "everything", "Everything"
    PEOPLE = "people", "People"
    UPDATES = "updates", "Blogs & news"
    PROJECTS = "projects", "Projects"
    EVENTS = "events", "Events"

    def model_class(self):
        mapping = {
            "everything": Page,
            "people": Profile,
            "updates": BlogPost,
            "projects": Project,
            "events": Event,
        }
        return mapping[self.value]

    def icon(self):
        mapping = {
            "everything": "doc",
            "people": "person",
            "updates": "blog",
            "projects": "folder",
            "events": "cal",
        }
        return mapping[self.value]


class SiteSearchForm(forms.Form):
    """Search form for finding pages across the site."""

    # keyword query
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": "Search by keyword or phrase",
            }
        ),
    )

    # filter to different page types
    filter = forms.ChoiceField(choices=SiteSearchFilters.choices, required=False)

    @staticmethod
    def filter_choices():
        return SiteSearchFilters
