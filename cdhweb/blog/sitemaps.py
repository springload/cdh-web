from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from cdhweb.blog.models import BlogPost


class BlogListSitemap(Sitemap):
    '''Sitemap for block views that are neither Wagtail pages nor
    tied to models (currently event recent and archive list views).'''

    def items(self):
        # return list of tuples for identifying blog list views
        # - could be url name, year, or year + month
        # factory = RequestFactory()

        items = [
            ('list',)
        ]

        live_posts = BlogPost.objects.live()
        for date in live_posts.dates('first_published_at', 'year',
                                     order='DESC'):
            items.append((date.year,))

        for date in live_posts.dates('first_published_at', 'month',
                                     order='DESC'):
            items.append((date.year, date.month))
        return items

    def location(self, obj):
        # determine url to generate based on length/content
        # two args — year/month archive
        if len(obj) == 2:
            return reverse('blog:by-month', kwargs={'year': obj[0],
                                                    'month': '%02d' % obj[1]})
        # single arg, numeric — year archive
        elif str(obj[0]).isdigit():
            return reverse('blog:by-year', args=obj)
        # non-numeric — named url
        else:
            return reverse('blog:%s' % obj[0])

        return obj[0]

    def lastmod(self, obj):
        posts = BlogPost.objects.live().order_by('-first_published_at')
        # if first element is numeric, filter by year
        if str(obj[0]).isdigit():
            posts = posts.filter(first_published_at__year=obj[0])
        # if two args, also filter by month
        if len(obj) == 2:
            posts = posts.filter(first_published_at__month=obj[1])

        return posts.first().first_published_at
