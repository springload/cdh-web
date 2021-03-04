import json
import datetime

import pytest
from django.core.exceptions import ValidationError
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.utils import timezone
from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from wagtail.tests.utils.form_data import rich_text

from cdhweb.pages.models import PageIntro, LinkPage
from cdhweb.people.models import PeopleLandingPage, Person, Profile
from cdhweb.blog.models import BlogPost, Author


class TestPeopleLandingPage(WagtailPageTests):

    def test_parent_pages(self):
        """no allowed parent page type; must be created manually"""
        self.assertAllowedParentPageTypes(PeopleLandingPage, [])

    def test_child_pages(self):
        """only profile pages and link pages can be children"""
        self.assertAllowedSubpageTypes(
            PeopleLandingPage, [Profile, LinkPage])


class TestProfile:

    def setUp(self, people_landing_page):
        """create person for testing"""
        self.person = Person.objects.create(
            first_name="tom", last_name="jones")

    def test_can_create(self, people_landing_page):
        """should be creatable as child of people landing page"""
        profile = Profile(
            title="tom r. jones",
            person=self.person,
            education=rich_text("school"),
            bio=json.dumps([{"type": "paragraph", "value": "about me"}])
        )
        people_landing_page.add_child(instance=profile)
        people_landing_page.save()
        assert self.person.profile == profile

    def test_person_required(self, people_landing_page):
        """profile page must be for an existing person"""
        with pytest.raises(ValidationError):
            people_landing_page.add_child(instance=Profile(
                title="tom r. jones",
                education=rich_text("school"),
                bio=json.dumps([{"type": "paragraph", "value": "about me"}])
            ))

    def test_delete_handler(self, people_landing_page):
        """deleting person should delete corresponding profile"""
        people_landing_page.add_child(instance=Profile(
            title="tom r. jones",
            person=self.person,
        ))
        people_landing_page.save()
        self.person.delete()
        assert Profile.objects.count() == 0

    def test_recent_blogposts(self, people_landing_page, blog_link_page):
        """profile should have person's most recent blog posts in context"""
        # FIXME create a user since BlogPost still currently assoc. with User
        User = get_user_model()
        tom = User.objects.create_user(username="tom")
        self.person.user = tom

        # create the profile page
        profile = Profile(
            title="tom jones",
            slug="tom-jones",
            person=self.person,
        )
        people_landing_page.add_child(instance=profile)
        people_landing_page.save()

        # context obj with blog posts is empty
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert not context["recent_posts"]  # empty list

        # create some blog posts by this person
        # "one"     2021-01-01  published
        # "two"     2021-01-02  published
        # "three"   2021-01-03  published
        # "four"    2021-01-04  draft
        # "five"    2021-01-05  published
        posts = {}
        for i, title in enumerate(["one", "two", "three", "four", "five"]):
            post = BlogPost(title=title)
            post.first_published_at = timezone.make_aware(
                datetime.datetime(2021, 1, i + 1))
            blog_link_page.add_child(instance=post)
            blog_link_page.save()
            Author.objects.create(post=post, person=tom)
            posts[title] = post
        posts["four"].unpublish()

        # only 3 most recent published posts should be in context
        # "five", "three", "two"
        factory = RequestFactory()
        request = factory.get(profile.get_url())
        context = profile.get_context(request)
        assert posts["five"] in context["recent_posts"]
        assert posts["three"] in context["recent_posts"]
        assert posts["two"] in context["recent_posts"]
        assert posts["four"] not in context["recent_posts"]
        assert posts["one"] not in context["recent_posts"]


class TestProfilePage(WagtailPageTests):

    def test_parent_pages(self):
        """only allowed parent is people landing page"""
        self.assertAllowedParentPageTypes(Profile, [PeopleLandingPage])

    def test_child_pages(self):
        """no allowed children"""
        self.assertAllowedSubpageTypes(Profile, [])


@pytest.mark.django_db
class TestPageIntro:

    def test_str(self):
        root = Page.objects.get(title="Root")
        link_page = LinkPage(title='Students', link_url='people/students')
        root.add_child(instance=link_page)
        intro = PageIntro.objects.create(
            page=link_page, paragraph='<p>We have great students</p>')

        assert str(intro) == link_page.title
