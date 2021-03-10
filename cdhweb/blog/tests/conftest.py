import json
from datetime import timedelta, datetime

import pytest
from django.utils import timezone

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
    """an announcement published yesterday with no author"""
    yesterday = timezone.now() - timedelta(days=1)
    post = BlogPost(
        title="A Big Announcement!",
        body=json.dumps([{
            "type": "paragraph",
            "value": "<p>here's the text of the announcement</p>"
        }])
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = yesterday
    post.save()
    return post


@pytest.fixture
def project_feature(db, blog_link_page, grad_pm):
    """a post about a sponsored project published 4 weeks ago with one author"""
    one_month_ago = timezone.now() - timedelta(weeks=4)
    post = BlogPost(
        title="Making progress on the Cool Project",
        body=json.dumps([{
            "type": "paragraph",
            "value": "<p>the Cool Project is getting cooler every day</p>"
        }])
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = one_month_ago
    post.save()
    Author.objects.create(person=grad_pm, post=post)
    return post


@pytest.fixture
def article(db, blog_link_page, staffer, postdoc):
    """an article by a staff member and a postdoc from 2019; updated in 2020"""
    in_2019 = timezone.make_aware(datetime(2019, 3, 4, 8, 25))
    in_2020 = timezone.make_aware(datetime(2020, 1, 15, 20, 12))
    post = BlogPost(
        title="We wrote an article together, and it got published on the CDH website",
        body=json.dumps([{
            "type": "paragraph",
            "value": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum."
        }])
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = in_2019
    post.last_published_at = in_2020
    post.save()
    Author.objects.create(person=staffer, post=post)
    Author.objects.create(person=postdoc, post=post)
    return post


@pytest.fixture
def blog_posts(db, announcement, project_feature, article):
    """convenience fixture to create several blog posts for testing"""
    return {
        "announcement": announcement,
        "project_feature": project_feature,
        "article": article
    }
