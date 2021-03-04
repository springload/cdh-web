import json
from datetime import timedelta

import pytest
from django.utils import timezone

from cdhweb.people.models import Person
from cdhweb.blog.models import BlogLinkPage, BlogPost, Author


@pytest.fixture
def blog_link_page(db, homepage):
    """create a test blog link page underneath the homepage"""
    link = BlogLinkPage(title="updates", link_url="updates")
    homepage.add_child(instance=link)
    homepage.save()
    return link


@pytest.fixture
def announcement(db, blog_link_page):
    """an announcement published yesterday with no specific author (CDH Staff)"""
    yesterday = timezone.now() - timedelta(days=1)
    post = BlogPost(
        title="A Big Announcement!",
        content=json.dumps([{
            "type": "paragraph",
            "value": "<p>here's the text of the announcement</p>"
        }])
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = yesterday
    post.save()
    cdh_staff = Person.objects.get_or_create(first_name="CDH Staff")[0]
    Author.objects.create(person=cdh_staff, post=post)
    return post


@pytest.fixture
def project_feature(db, blog_link_page, staffer):
    """a post about a sponsored project published 4 weeks ago with one author"""
    one_month_ago = timezone.now() - timedelta(weeks=4)
    post = BlogPost(
        title="Making progress on the Cool Project",
        content=json.dumps([{
            "type": "paragraph",
            "value": "<p>the Cool Project is getting cooler every day</p>"
        }])
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = one_month_ago
    post.save()
    Author.objects.create(person=staffer, post=post)
    return post


@pytest.fixture
def blog_posts(db, announcement, project_feature):
    """convenience fixture to create several blog posts for testing"""
    return {
        "announcement": announcement,
        "project_feature": project_feature
    }
