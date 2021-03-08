from cdhweb.blog.models import BlogPost


class TestAuthor:

    def test_str(self, project_feature):
        """author should be identified by person and post"""
        author = project_feature.authors.first()
        assert str(author) == "Staffer on \"Making progress on the Cool Project\" (%s)" % \
            project_feature.first_published_at


class TestBlogPostQuerySet:

    def test_featured(self, blog_posts):
        """should query blog posts by featured status"""
        # no posts are featured initially
        assert not BlogPost.objects.featured().exists()
        # feature one
        post = BlogPost.objects.order_by("?").first()
        post.is_featured = True
        post.save()
        # should be returned in queryset
        assert BlogPost.objects.featured().count() == 1
