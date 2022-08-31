from django.db.models import Case, Max, Value, When
from django.db.models.functions import Greatest
from django.shortcuts import render
from django.urls import reverse
from django.views.generic.list import ListView

from cdhweb.pages.views import LastModifiedListMixin
from cdhweb.people.models import Person, PersonQuerySet


class PersonListView(ListView, LastModifiedListMixin):
    """Base class for person list views"""

    model = Person
    lastmodified_attr = "updated_at"

    #: title for this category of people
    page_title = ""
    #: title for non-past people in this category of people
    current_title = ""
    #: label for past people in this category of people
    past_title = ""

    def get_queryset(self):
        # get people ordered by position (job title then start date)
        return super().get_queryset().order_by_position().distinct()

    def get_current(self):
        """Get current people from the queryset. Override to customize
        which filter is used. By default, uses generic current logic that
        checks both positions and grants."""
        return self.object_list.current()

    def get_past(self):
        """Get past people. Override to customize filters and ordering. By
        default, assumes any profiles that aren't current are past."""
        current = self.get_current()
        return self.object_list.exclude(id__in=current.values("id"))

    def grant_label(self, grant):
        """Convert a grant into a label with date."""
        # if a fellowship, display as "X fellow"
        if "Fellow" in grant.grant_type.grant_type:
            no_ship = grant.grant_type.grant_type.split("ship", 1)[0]
            return f"{grant.years} {no_ship}"
        # otherwise "X grant recipient"
        return f"{grant.years} {grant.grant_type.grant_type} Grant Recipient"

    def display_label(self, person):
        # no default; force subclasses to implement
        raise NotImplementedError

    def add_display_label(self, queryset):
        # annotate the queryset with label to be displayed for this view
        for person in queryset:
            person.label = self.display_label(person)
        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        # update context to display current and past people separately
        current = self.get_current()
        # filter past based current ids, rather than trying to do the complicated
        # query to find not current people
        past = self.get_past()
        context.update(
            {
                "current": self.add_display_label(current),
                "past": self.add_display_label(past),
                "page_title": self.page_title,
                "past_title": self.past_title,
                "current_title": self.current_title
                or self.page_title,  # use main title as default
                "archive_nav_urls": [
                    ("Staff", reverse("people:staff")),
                    ("Students", reverse("people:students")),
                    ("Affiliates", reverse("people:affiliates")),
                    ("Executive Committee", reverse("people:exec-committee")),
                ],
            }
        )
        return context


class StaffListView(PersonListView):
    """Display current and past CDH staff"""

    page_title = "Staff"
    past_title = "Past Staff"

    def display_label(self, person):
        # for staff list view, label based on most recent position
        last_position = person.positions.first()
        label = last_position.title
        # if position is not current, include years
        if not last_position.is_current:
            label = "%s %s" % (last_position.years, label)
        return label

    def get_queryset(self):
        # filter to profiles with staff flag set and exclude students
        # (already ordered by job title sort order and then by last name)
        return super().get_queryset().cdh_staff().not_students()
        # NOTE: if someone goes from a student role to a staff role, they need
        # to have their PU status changed to something that's not a student
        # in order to not be excluded from this page based on their previous
        # role

    def get_current(self):
        # we only care about current position, grant doesn't matter;
        # filter out past faculty directors who are current exec members
        return self.object_list.current_position_nonexec()


# yet another special case for labels/membership
HUM_DATASCI = "Humanities + Data Science Institute"


class StudentListView(PersonListView):
    """Display current and past graduate fellows, graduate and undergraduate
    assistants."""

    page_title = "Students"
    past_title = "Alumni"

    def get_queryset(self):
        # filter to just students
        return (
            super()
            .get_queryset()
            .student_affiliates()
            .grant_years()
            .project_manager_years()
        )
        # FIXME: still getting some duplicates...

    def display_label(self, person):
        # for student assistants and fellows, label based on position
        # students can multiple affiliations
        labels = []
        current_label = None
        for position in person.positions.all():
            label = str(position.title)
            # if position is current, set as current label
            if position.is_current:
                current_label = label
            # if not current, include years and add to list
            else:
                label = "%s %s" % (position.years, label)
                labels.append(label)

        if person.latest_grant:
            # if student was a project director, show as grant recipient/fellow
            grant = person.latest_grant
            label = self.grant_label(grant)
            if grant.is_current:
                current_label = label
            else:
                labels.append(label)

        # for students on projects, label based on project membership
        roles = set(PersonQuerySet.project_roles + PersonQuerySet.affiliate_roles) - {
            "Project Director"
        }
        for membership in person.membership_set.filter(role__title__in=roles):
            # NOTE: it might be better to use memberships for
            # project director / grant role as well, but with the new
            # data model it's harder to determine what type of grant they were on
            label = membership.role.title
            # if in humanities data science, use title + role
            if membership.project.title == HUM_DATASCI:
                label = "%s %s" % (HUM_DATASCI, label)
            if membership.is_current:
                current_label = label
            else:
                label = "%s %s" % (membership.years, label)
                labels.append(label)

        # if the student has a current affiliation, return only that
        # otherwise return multiple
        # NOTE: could truncate this list and/or prioritize certain titles/roles
        return current_label or "\n".join(sorted(set(labels), reverse=True))
        # NOTE: at least one case is generating duplicate labels,
        # not sure why!

    def get_past(self):
        # show most recent first based on grant or position end date
        # NOTE the use of Case/When here is to avoid Greatest() returning NULL
        # if any of its arguments are NULL, which is mysql behavior:
        # https://docs.djangoproject.com/en/2.2/ref/models/database-functions/#django.db.models.functions.Greatest
        # see also the django docs on conditional aggregation:
        # https://docs.djangoproject.com/en/1.11/ref/models/conditional-expressions/#conditional-aggregation
        # NOTE also that this causes dates to be interpreted as strings in QA;
        # relevant ticket: https://code.djangoproject.com/ticket/30224
        return (
            super()
            .get_past()
            .annotate(
                most_recent=Greatest(
                    Case(
                        When(
                            membership__end_date__isnull=False,
                            then=Max("membership__end_date"),
                        ),
                        default=Value("1900-01-01"),
                    ),
                    Case(
                        When(
                            positions__end_date__isnull=False,
                            then=Max("positions__end_date"),
                        ),
                        default=Value("1900-01-01"),
                    ),
                )
            )
            .order_by("-most_recent")
        )


class AffiliateListView(PersonListView):
    """Display current and past faculty & staff affiliates"""

    page_title = "Affiliates"
    past_title = "Past {}".format(page_title)

    def get_queryset(self):
        # filter to affiliates, annotate with grant years, and order by name
        return super().get_queryset().affiliates().grant_years().order_by("last_name")

    def display_label(self, person):
        # use grant information or membership role for label
        mship = person.membership_set.first()  # is this reliable?
        # special case; use grant + role
        if mship.project.title == HUM_DATASCI:
            return "%s %s" % (HUM_DATASCI, person.membership_set.first().role.title)

        return self.grant_label(person.latest_grant)

    def get_current(self):
        # we only care about current grants, position doesn't matter
        return self.object_list.current_grant()


class ExecListView(PersonListView):
    """Display current and past executive committee members."""

    page_title = "Executive Committee"
    past_title = "Past members of {}".format(page_title)

    def get_queryset(self):
        # filter to exec members
        return super().get_queryset().executive_committee().order_by("last_name")

    def get_current(self):
        # we only care about current position, grant doesn't matter
        return self.object_list.current_position()

    def display_label(self, person):
        # for exec, we just want to show their job title
        return person.job_title

    def get_context_data(self):
        context = super().get_context_data()
        # executive committee needs an additional filter:
        # exec members, sits with committee, then alumni as usual
        current = context["current"]
        context.update(
            {
                "current": self.add_display_label(current.exec_member()),
                "sits_with": self.add_display_label(current.sits_with_exec()),
            }
        )
        return context


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
