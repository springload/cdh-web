from django.urls import reverse
from wagtail.contrib.redirects.models import Redirect


class TestHooks:
    def test_create_redirect_on_slug_change(db, admin_client, content_page):
        """redirect should automatically be created on slug change"""
        assert Redirect.objects.count() == 0
        old_path = content_page.url[:-1]
        # Change the page's slug by making a POST request; note that we have to
        # fake all the relevant data from the page's edit form. See also:
        # https://github.com/wagtail/wagtail/blob/de9588590bbabffbbe30e8830d34b59d8da6512e/wagtail/admin/tests/pages/test_create_page.py#L941-L970
        admin_client.post(
            reverse("wagtailadmin_pages:edit", args=(content_page.pk,)),
            {
                "title": content_page.title,
                "slug": "new-title",    # change slug
                "body-count": "1",
                "body-0-deleted": "",
                "body-0-order": "0",
                "body-0-type": "text",
                "body-0-value": content_page.body[0].value,
                "attachments-count": "0",
                "action-publish": "Publish",
            },
        )
        # Redirect should be created pointing from old path to current page
        assert Redirect.objects.filter(
            old_path=old_path, redirect_page=content_page
        ).exists()
