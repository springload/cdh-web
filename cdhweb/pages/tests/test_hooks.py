from django.urls import reverse
from wagtail.contrib.redirects.models import Redirect
from wagtail.core import hooks


class TestHooks:
    def test_create_redirect_on_slug_change(db, rf, content_page):
        """redirect should automatically be created on slug change"""
        assert Redirect.objects.count() == 0
        # get the registered hook so we can call it manually to simulate edit
        hook_fn = hooks.get_hooks("before_edit_page")[0]
        request = rf.post(
            reverse("wagtailadmin_pages:edit", args=(content_page.id,)),
            {"slug": "new-slug"},  # fake changing the slug
        )
        hook_fn(request=request, page=content_page)
        # should redirect old slug to current version of page
        assert Redirect.objects.filter(
            old_path="/landing/content", redirect_page=content_page
        ).exists()
