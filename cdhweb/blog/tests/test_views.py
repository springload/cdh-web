from django.urls import reverse
from mezzanine.core.models import CONTENT_STATUS_DRAFT

from cdhweb.blog.models import BlogPost
from cdhweb.blog.views import AtomBlogPostFeed, RssBlogPostFeed


class TestViews:

    def test_rss_feed(self):
        post = BlogPost.objects.get(pk=1)

        response = self.client.get(reverse('blog:rss'))
        assert response['content-type'] == 'application/rss+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)
        # check for post content
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, post.content[:100])

        # post with author
        authorpost = BlogPost.objects.filter(users__isnull=False).first()
        self.assertContains(response, str(authorpost.users.first()))

        # draft post should *NOT* be included
        post.status = CONTENT_STATUS_DRAFT
        post.save()
        response = self.client.get(reverse('blog:rss'))
        self.assertNotContains(response, post.get_absolute_url())

        # TODO: author with published profile page, multiple authors

    def test_atom_feed(self):
        response = self.client.get(reverse('blog:atom'))
        assert response['content-type'] == 'application/atom+xml; charset=utf-8'
        self.assertContains(response, RssBlogPostFeed.title)
        self.assertContains(response, RssBlogPostFeed.description)

    def test_index(self):
        response = self.client.get(reverse('blog:list'))

        # title displays
        self.assertContains(response, 'Latest Updates')

        for post in BlogPost.objects.published():
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())
            self.assertContains(response, post.description)
            for auth in post.users.all():
                self.assertContains(response, str(auth))

            # links to blog archive by montth
            self.assertContains(response,
                                reverse('blog:by-month', kwargs={'year': post.publish_date.year,
                                                                 'month': post.publish_date.strftime('%m')}))

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

    def test_blogpost_detail(self):
        post = BlogPost.objects.order_by('publish_date').first()
        second_post = BlogPost.objects.order_by('publish_date')[1]
        response = self.client.get(post.get_absolute_url())

        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, post.description)
        for auth in post.users.all():
            self.assertContains(response, str(auth))

        self.assertContains(response, ', '.join(post.keywords.all()))

        # keywords & description in header
        self.assertContains(response,
                            '<meta name="keywords" content="%s"/>' % ', '.join(post.keywords.all()))
        self.assertContains(response,
                            '<meta name="description" content="%s"/>' % post.description)

        # feed links should occur twice: once in header, once in body
        self.assertContains(response, reverse('blog:rss'), count=2)
        self.assertContains(response, reverse('blog:atom'), count=2)

        # next/previous links
        # first post has next and no previous
        self.assertContains(response, second_post.title)
        self.assertContains(response, second_post.get_absolute_url())
        self.assertContains(response, 'rel="next"')
        self.assertNotContains(response, 'rel="prev"')

        # second post has previous and no next
        response = self.client.get(second_post.get_absolute_url())
        self.assertContains(response, post.title)
        self.assertContains(response, post.get_absolute_url())
        self.assertContains(response, 'rel="prev"')
        self.assertNotContains(response, 'rel="next"')

    def test_blogs_by_year(self):
        response = self.client.get(
            reverse('blog:by-year', kwargs={'year': 2017}))

        assert response.context['title'] == '2017'
        # date-specific title displays
        self.assertContains(response, '2017 Updates')
        # links to blog archive by montth
        self.assertContains(response,
                            reverse('blog:by-month', kwargs={'year': 2017, 'month': '09'}))

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.published().filter(publish_date__year=2017):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.published().exclude(publish_date__year=2017):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())

    def test_blogs_by_month(self):
        response = self.client.get(reverse('blog:by-month',
                                           kwargs={'year': 2017, 'month': '09'}))

        assert response.context['title'] == 'September 2017'
        # date-specific title displays
        self.assertContains(response, 'September 2017 Updates')

        # date filtering is really django logic, this is just
        # a sanity check for display
        for post in BlogPost.objects.filter(publish_date__year=2017,
                                            publish_date__month=9):
            self.assertContains(response, post.title)
            self.assertContains(response, post.get_absolute_url())

        for post in BlogPost.objects.exclude(publish_date__year=2017,
                                             publish_date__month=9):
            self.assertNotContains(response, post.title)
            self.assertNotContains(response, post.get_absolute_url())
