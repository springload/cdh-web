from cdhweb.blog.models import BlogPost
from cdhweb.resources.sitemaps import PublishedItemSitemap


class BlogPostSitemap(PublishedItemSitemap):
    model = BlogPost

    def priority(self, item):
        if item.is_featured:
            return 0.6
