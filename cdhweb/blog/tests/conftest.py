import zoneinfo
from datetime import timezone as tz

import pytest
from django.utils import timezone

from cdhweb.blog.models import Author, BlogLinkPageArchived, BlogPost
from cdhweb.pages.tests.conftest import to_streamfield_safe

EST = zoneinfo.ZoneInfo("America/New_York")


def make_blog_link_page(homepage):
    """Create a test blog link page underneath the homepage."""
    link = BlogLinkPageArchived(title="updates", link_url="updates")
    homepage.add_child(instance=link)
    homepage.save()
    return link


def make_announcement(blog_link_page):
    """Create an announcement published in 2020 with no author."""
    pubdate = timezone.datetime(2020, 11, 2, 15, tzinfo=EST).astimezone(tz.utc)
    post = BlogPost(
        title="A Big Announcement!",
        body=to_streamfield_safe(
            "<p>We're making a big digital humanities announcement.</p>"
        ),
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = pubdate
    post.last_published_at = pubdate
    post.save()
    return post


def make_project_feature(blog_link_page, grad_pm):
    """Create a sponsored project feature by a grad PM published in 2018."""
    pubdate = timezone.datetime(2018, 5, 19, 17, 31, tzinfo=EST).astimezone(tz.utc)
    post = BlogPost(
        title="Making progress on the Cool Project",
        body=to_streamfield_safe(
            "<p>the Cool Digital Project is getting cooler every day</p>"
        ),
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = pubdate
    post.last_published_at = pubdate
    post.save()
    Author.objects.create(person=grad_pm, post=post)
    return post


def make_article(blog_link_page, staffer, postdoc):
    """Create article by staff member and postdoc from 2019; updated in 2020"""
    in_2019 = timezone.datetime(2019, 3, 4, 8, 25, tzinfo=EST).astimezone(tz.utc)
    in_2020 = timezone.datetime(2020, 1, 15, 20, 12, tzinfo=EST).astimezone(tz.utc)
    post = BlogPost(
        title="We wrote an article together, and it got published on the CDH website",
        body=to_streamfield_safe(
            "<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>"
        ),
    )
    blog_link_page.add_child(instance=post)
    blog_link_page.save()
    post.first_published_at = in_2019
    post.last_published_at = in_2020
    post.save()
    Author.objects.create(person=staffer, post=post)
    Author.objects.create(person=postdoc, post=post)
    return post


def make_blog_posts(blog_link_page, grad_pm, staffer, postdoc):
    """Create a variety of blog posts."""
    return {
        "announcement": make_announcement(blog_link_page),
        "project_feature": make_project_feature(blog_link_page, grad_pm),
        "article": make_article(blog_link_page, staffer, postdoc),
    }


@pytest.fixture
def blog_link_page(db, homepage):
    return make_blog_link_page(homepage)


@pytest.fixture
def announcement(db, blog_link_page):
    return make_announcement(blog_link_page)


@pytest.fixture
def project_feature(db, blog_link_page, grad_pm):
    return make_project_feature(blog_link_page, grad_pm)


@pytest.fixture
def article(db, blog_link_page, staffer, postdoc):
    return make_article(blog_link_page, staffer, postdoc)


@pytest.fixture
def blog_posts(db, announcement, project_feature, article):
    return {
        "announcement": announcement,
        "project_feature": project_feature,
        "article": article,
    }
