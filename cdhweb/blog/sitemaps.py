from cdhweb.blog.models import OldBlogPost
from cdhweb.resources.sitemaps import PublishedItemSitemap


class BlogPostSitemap(PublishedItemSitemap):
    model = OldBlogPost

    def priority(self, item):
        if item.is_featured:
            return 0.6
