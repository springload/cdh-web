from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from mezzanine.pages.models import RichTextPage
from mezzanine.core.models import CONTENT_STATUS_DRAFT, CONTENT_STATUS_PUBLISHED


class TestDraftPageIndicator(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    def test_draft_page(self):
        # body should have classes "richtextpage draft"
        page = RichTextPage(title="my draft page", status=CONTENT_STATUS_DRAFT)
        page.save()
        request = self.factory.get(page.get_absolute_url())
        request.user = AnonymousUser()
        response = render(request, 'pages/richtextpage.html', {'page': page})
        self.assertContains(response, '<body class="richtextpage draft">')

    def test_published_page(self):
        # body should just have class "richtextpage"
        page = RichTextPage(title="my draft page",
                            status=CONTENT_STATUS_PUBLISHED)
        page.save()
        request = self.factory.get(page.get_absolute_url())
        request.user = AnonymousUser()
        response = render(request, 'pages/richtextpage.html', {'page': page})
        self.assertContains(response, '<body class="richtextpage">')
