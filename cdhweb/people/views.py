from django.db.models import Case, DateField, Max, Value, When
from django.db.models.functions import Greatest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.list import ListView

from cdhweb.pages.views import LastModifiedListMixin
from cdhweb.people.models import Person, PersonQuerySet


def speakerlist_gone(request):
    # return 410 gone for speakers list view;
    # (removed in 3.0, no longer needed after the Year of Data)
    return render(
        request,
        "404.html",
        context={
            "error_code": 410,
            "message": "That page isn't here anymore.",
            "page_title": "Error — no longer available",
        },
        status=410,
    )
