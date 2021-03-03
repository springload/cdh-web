from datetime import datetime, timedelta

from django.utils import timezone

from cdhweb.blog.models import BlogPost


class TestBlog:

    def test_get_absolute_url(self):
        jan15 = datetime(2016, 1, 15)
        post = BlogPost(publish_date=jan15, slug='news-and-updates')
        # single-digit months should be converted to two-digit for url
        resolved_url = post.get_absolute_url()
        assert resolved_url.namespace == 'blog'
        assert resolved_url.url_name == 'detail'
        assert resolved_url.kwargs['year'] == str(post.publish_date.year)
        assert resolved_url.kwargs['month'] == '%02d' % post.publish_date.month
        assert resolved_url.kwargs['slug'] == post.slug

    def test_short_title(self):
        '''test that truncated titles are correctly generated'''
        # truncate with ellipsis for titles > 75char
        post = BlogPost(
            title="Congratulations to Valedictorian Jin Yun Chow '17 and Salutatorian Grant Storey '17")
        assert len(post.short_title) == 65
        assert post.short_title.endswith('…')
        # do nothing for titles < 75char
        post = BlogPost(title="Congratulations!")
        assert post.short_title == post.title

    def test_short_description(self):
        '''test that truncated descriptions are correctly generated'''
        # truncate with ellipsis for descriptions > 250char
        post = BlogPost(description="The CDH is hiring! \u00a0We are looking for a curious, committed, and collegial colleague to join our Development and Design Team as our second Digital Humanities\u00a0Developer. You will work with database designers, UX designers, project managers, fellow programmers\u00a0and the faculty, students and staff of Princeton University to create innovating\u00a0projects and contribute back to the Open Source software community. \u00a0")
        assert len(post.short_description) == 250
        assert post.short_description.endswith('…')
        # do nothing for descriptions < 250char
        post = BlogPost(description="The CDH is hiring!")
        assert post.short_description == post.description


class TestBlogPostQuerySet:

    def test_featured(self):
        post = BlogPost.objects.create()

        assert not BlogPost.objects.featured().exists()

        post.is_featured = True
        post.save()
        assert BlogPost.objects.featured().exists()

    def test_recent(self):
        # use django timezone util for timezone-aware datetime
        yesterday = timezone.now() - timedelta(days=1)
        oldest = timezone.now() - timedelta(days=10)
        today_post = BlogPost.objects.create(publish_date=timezone.now())
        yesterday_post = BlogPost.objects.create(publish_date=yesterday)
        oldest_post = BlogPost.objects.create(publish_date=oldest)

        recent = list(BlogPost.objects.recent())
        # most recent listed first
        assert today_post == recent[0]
        assert yesterday_post == recent[1]
        assert oldest_post == recent[2]
