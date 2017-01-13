from django.test import TestCase

from datetime import datetime
from .models import BlogPost


class TestBlog(TestCase):

    def test_get_absolute_url(self):
        jan15 = datetime(2016, 1, 15)
        post = BlogPost(publish_date=jan15, slug='news-and-updates')
        # single-digit months should be converted to two-digit for url
        assert post.get_absolute_url().endswith('/2016/01/news-and-updates/')

