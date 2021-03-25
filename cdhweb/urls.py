from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic.base import RedirectView, TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.contrib.sitemaps.views import sitemap
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls


admin.autodiscover()

# use test favicon when test warning is enabled as another visual indicator
FAVICON = '/static/favicon.ico'
if getattr(settings, 'SHOW_TEST_WARNING', False):
    FAVICON = '/static/favicon-test.ico'

urlpatterns = [
    # admin site
    path("admin/", include(admin.site.urls)),

    # special paths
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
                                                   content_type='text/plain')),
    re_path(r'^favicon\.ico$', RedirectView.as_view(
        url=FAVICON, permanent=True)),

    # main apps
    path("people/", include("cdhweb.people.urls", namespace='people')),
    path("updates/", include("cdhweb.blog.urls", namespace='blog')),
    path("events/", include("cdhweb.events.urls", namespace='event')),
    path("projects/", include("cdhweb.projects.urls", namespace='projects')),

    # CAS login urls
    path("accounts/", include('pucas.cas_urls')),

    # - all blog urls are now under updates/
    re_path(r'^blog(?P<blog_url>.*)$',
            RedirectView.as_view(url='/updates%(blog_url)s', permanent=True)),

    # sitemaps
    path("sitemap.xml", sitemap),

    # wagtail paths
    # NOTE temporarily make wagtail pages available at pages/ so that they can
    # coexist with mezzanine urls
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    # enable if needed to test mezzanine pages
    # path("mezz", include("mezzanine.urls")),

    path("", include(wagtail_urls)),
]

# serve static files in development - automatically activates in DEBUG; see
# https://docs.djangoproject.com/en/3.1/howto/static-files/#serving-files-uploaded-by-a-user-during-development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Adds ``STATIC_URL`` to the context of error pages, so that error
# pages can use JS, CSS and images.
handler404 = "mezzanine.core.views.page_not_found"
handler500 = "mezzanine.core.views.server_error"
