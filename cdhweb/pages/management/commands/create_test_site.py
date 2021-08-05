from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from cdhweb.conftest import (
    make_blog_link_page,
    make_blog_posts,
    make_content_page,
    make_events,
    make_events_link_page,
    make_homepage,
    make_landing_page,
    make_people,
    make_people_landing_page,
    make_projects,
    make_projects_landing_page,
    make_staffer_profile,
    make_wagtail_site,
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        """Fill the database with models to approximate a real site."""
        # NOTE not idempotent! running more than once will duplicate models.

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
            people["grad_pm"],  # used to associate w/ post
            people["staffer"],
            people["postdoc"],
        )
