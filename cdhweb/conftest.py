"""Fixtures/utilities that should be globally available for testing."""
# FIXME not sure how else to share fixtures that depend on other fixtures
# between modules - if you import just the top-level fixture (e.g. "events"),
# it fails to find the fixture dependencies, and so on all the way down. For
# now this does what we want, although it pollutes the namespace somewhat
from cdhweb.pages.tests.conftest import *
from cdhweb.events.tests.conftest import *
from cdhweb.projects.tests.conftest import *
from cdhweb.people.tests.conftest import *
from cdhweb.blog.tests.conftest import *


def make_test_site():
    """Populate the entire database using fixture functions, for e2e tests."""
    from django.contrib.sites.models import Site

    # NOTE be careful of namespace pollution here! a ton of things are imported
    # above in order to be used in tests elsewhere, so you need to be careful
    # how things are named below to avoid collisions.

    # set default django site (not wagtail site) domain so sitemaps work
    django_site = Site.objects.get()
    django_site.domain = "localhost:8000"
    django_site.save()

    # set wagtail site port so page URL reversing works
    site = make_wagtail_site()
    site.port = 8000
    site.save()

    # pages
    home = make_homepage(site)
    landing = make_landing_page(home)
    make_content_page(landing)

    # projects
    projects_landing = make_projects_landing_page(home)
    make_projects(projects_landing)

    # people
    people_landing = make_people_landing_page(home)
    people = make_people(projects_landing)  # creates associated projects
    make_staffer_profile(people_landing, people["staffer"])

    # events
    event_link = make_events_link_page(home)
    make_events(event_link)

    # blog
    blog_link = make_blog_link_page(home)
    make_blog_posts(
        blog_link,
        people["grad_pm"],
        people["staffer"],
        people["postdoc"],
    )
