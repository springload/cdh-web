from cdhweb.blog.models import BlogPost


class TestAuthor:
    def test_str(self, article):
        """author should be identified by person and post"""
        author = article.authors.first()
        assert (
            str(author)
            == "Staffer on We wrote an article together, and it got published on the CDH website"
        )


class TestBlogPostQuerySet:
    def test_featured(self, blog_posts):
        """should query blog posts by featured status"""
        # no posts are featured initially
        assert not BlogPost.objects.featured().exists()
        # feature one
        post = BlogPost.objects.order_by("?").first()
        post.featured = True
        post.save()
        # should be returned in queryset
        assert BlogPost.objects.featured().count() == 1
