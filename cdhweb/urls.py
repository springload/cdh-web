from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import serve
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic.base import RedirectView, TemplateView
from django.views.i18n import set_language
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from cdhweb.blog.sitemaps import BlogPostSitemap
from cdhweb.events.sitemaps import EventSitemap
from cdhweb.people.sitemaps import ProfileSitemap
from cdhweb.projects.sitemaps import ProjectSitemap
from cdhweb.resources import views as resource_views
from cdhweb.resources.sitemaps import PageSitemap

admin.autodiscover()

# Add the urlpatterns for any custom Django applications here.
# You can also change the ``home`` view to add your own functionality
# to the project's homepage.

urlpatterns = i18n_patterns(
    # Change the admin prefix here to use an alternate URL for the
    # admin interface, which would be marginally more secure.
    url("^admin/", include(admin.site.urls)),
)

if settings.USE_MODELTRANSLATION:
    urlpatterns += [
        url('^i18n/$', set_language, name='set_language'),
    ]

sitemaps = {
    'blogs': BlogPostSitemap,
    'events': EventSitemap,
    'pages': PageSitemap,
    'people': ProfileSitemap,
    'projects': ProjectSitemap,
}

# use test favicon when test warning is enabled as another visual indicator
FAVICON = '/static/favicon.ico'
if getattr(settings, 'SHOW_TEST_WARNING', False):
    FAVICON = '/static/favicon-test.ico'

urlpatterns += [
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
        content_type='text/plain')),
    url(r'^favicon\.ico$', RedirectView.as_view(url=FAVICON, permanent=True)),
    url("^people/", include("cdhweb.people.urls", namespace='people')),
    # actual blog url still TBD
    url("^updates/", include("cdhweb.blog.urls", namespace='blog')),
    url("^events/", include("cdhweb.events.urls", namespace='event')),
    url("^projects/", include("cdhweb.projects.urls", namespace='project')),

    url("^$", resource_views.Homepage.as_view(), name="home"),

    # CAS login urls
    url(r'^accounts/', include('pucas.cas_urls')),

    # programmatic redirects from v1 site
    # - old staff page is now under /people/
    url(r'^about/staff/(?P<slug>[\w-]+)/$',
        RedirectView.as_view(pattern_name='people:profile', permanent=True),
        name='old-profile'),
    # - all blog urls are now under updates/
    url(r'^blog(?P<blog_url>.*)$',
        RedirectView.as_view(url='/updates%(blog_url)s', permanent=True)),

    # override mezzanine sitemap and use locally customized sitemaps
    # NOTE: could use a sitemap index and grouped sitemaps here, but
    # may complicate testing with pa11y-ci
    url(r"^sitemap\.xml$", sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    # wagtail paths
    # NOTE temporarily make wagtail pages available at pages/ so that they can
    # coexist with mezzanine urls
    url(r'^cms/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),
    url(r'^pages/', include(wagtail_urls)),

    # let mezzanine handle everything else
    url("^", include("mezzanine.urls")),
]

if settings.DEBUG:
    # serve user-uploaded media in debug mode
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
