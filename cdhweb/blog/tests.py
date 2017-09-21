from datetime import datetime

from django.test import TestCase
from django.urls import resolve, reverse
from django.utils.html import escape

from cdhweb.blog.models import BlogPost
from cdhweb.blog.views import RssBlogPostFeed


class TestBlog(TestCase):

    def test_get_absolute_url(self):
        jan15 = datetime(2016, 1, 15)
        post = BlogPost(publish_date=jan15, slug='news-and-updates')
        # single-digit months should be converted to two-digit for url
        resolved_url = resolve(post.get_absolute_url())
        assert resolved_url.namespace == 'blog'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['year'] == str(post.publish_date.year)
        assert resolved_url.kwargs['month'] == '%02d' % post.publish_date.month
        assert resolved_url.kwargs['slug'] == post.slug


class TestViews(TestCase):
    fixtures = ['test_blogposts.json']

    def test_rss_feed(self):
        post = BlogPost.objects.first()

        response = self.client.get(reverse('blog:rss'))
        assert response['content-type'] == 'application/rss+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)
        # check for post content
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, escape(post.content[:100]))

    def test_atom_feed(self):
        response = self.client.get(reverse('blog:atom'))
        assert response['content-type'] == 'application/atom+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)

    def test_index(self):
        posts = BlogPost.objects.all()
        response = self.client.get(reverse('blog:list'))
        for post in posts:
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.description)
            for auth in post.users.all():
                self.assertContains(response, str(auth))

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

    def test_blogpost_detail(self):
        post = BlogPost.objects.first()
        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, post.description)
        for auth in post.users.all():
            self.assertContains(response, str(auth))

        self.assertContains(response, ', '.join(post.keywords.all()))

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)


