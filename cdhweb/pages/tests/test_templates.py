import pytest
from django.urls import reverse
from django.utils.dateformat import format
from pytest_django.asserts import (assertContains, assertTemplateNotUsed,
                                   assertTemplateUsed)

from cdhweb.pages.models import CaptionedImageBlock, SVGImageBlock


class TestHomePage:

    def test_visit(self, client, site, homepage):
        """homepage should be navigable"""
        response = client.get(homepage.relative_url(site))
        assert response.status_code == 200

    def test_page_content(self, client, site, homepage):
        """homepage editable content should display"""
        response = client.get(homepage.relative_url(site))
        assertContains(response, homepage.body[0].value.source)

    def test_empty_posts(self, client, site, homepage):
        """homepage should not render carousel if no blog posts exist"""
        response = client.get(homepage.relative_url(site))
        assertTemplateNotUsed(response, "snippets/carousel.html")

    def test_blog_posts(self, client, site, homepage, blog_posts):
        """homepage should display featured blog posts in carousel"""
        response = client.get(homepage.relative_url(site))
        assertTemplateUsed(response, "snippets/carousel.html")

        # no posts featured, so most recent ones should be in context
        assert len(response.context["updates"]) == 3

        # feature some posts; only those should be displayed
        announcement = blog_posts["announcement"]
        project_feature = blog_posts["project_feature"]
        announcement.featured = True
        project_feature.featured = True
        announcement.save()
        project_feature.save()
        response = client.get(homepage.relative_url(site))
        assert len(response.context["updates"]) == 2
        assert announcement in response.context["updates"]
        assert project_feature in response.context["updates"]

        # should display short title, short description, and link
        assertContains(response, announcement.short_title)
        assertContains(response, announcement.short_description)
        assertContains(response, announcement.get_url())

        # unpublished posts shouldn't be displayed
        announcement.unpublish()
        response = client.get(homepage.relative_url(site))
        assert announcement not in response.context["updates"]

    def test_empty_projects(self, client, site, homepage):
        """homepage should not render projects if none exist"""
        response = client.get(homepage.relative_url(site))
        assertTemplateNotUsed(response, "projects/snippets/project_card.html")

    def test_highlighted_projects(self, client, site, homepage, projects):
        """homepage should display highlighted projects as cards"""
        response = client.get(homepage.relative_url(site))

        # should be no projects in context, since none highlighted
        assert len(response.context["projects"]) == 0

        # highlight some projects; only those should be displayed
        derrida = projects["derrida"]
        pliny = projects["pliny"]
        derrida.highlight = True
        pliny.highlight = True
        derrida.save()
        pliny.save()
        response = client.get(homepage.relative_url(site))
        assert len(response.context["projects"]) == 2
        assert derrida in response.context["projects"]
        assert pliny in response.context["projects"]

        # should display title, short description, and link
        assertContains(response, derrida.short_description)
        assertContains(response, derrida.title)
        assertContains(response, derrida.get_url())

        # unpublished projects shouldn't be displayed
        derrida.unpublish()
        response = client.get(homepage.relative_url(site))
        assert derrida not in response.context["projects"]

    def test_empty_events(self, client, site, homepage):
        """homepage should display message when no events are available"""
        response = client.get(homepage.relative_url(site))
        assertTemplateNotUsed(response, "events/snippets/event_card.html")
        assertContains(response, "Next semester's events are being scheduled.")

    def test_upcoming_events(self, client, site, homepage, events):
        """homepage should display upcoming events as cards"""
        response = client.get(homepage.relative_url(site))

        # should have link to event list
        assertContains(response, reverse("events:upcoming"))

        # only one event in context, since others already happened
        assert len(response.context["events"]) == 1
        assert events["workshop"] not in response.context["events"]
        assert events["lecture"] not in response.context["events"]

        # shows event title, start/end time, and link to view
        assertContains(response, events["deadline"].get_url())
        assertContains(response, events["deadline"].title)
        assertContains(response, format(events["deadline"].start_time, "F j"))
        assertContains(response, format(events["deadline"].end_time, "j"))

        # shouldn't show if not published
        events["deadline"].unpublish()
        response = client.get(homepage.relative_url(site))
        assert events["deadline"] not in response.context["events"]


class TestLandingPage:

    def test_visit(self, client, site, landing_page):
        """landingpage should be navigable"""
        response = client.get(landing_page.relative_url(site))
        assert response.status_code == 200

    def test_page_content(self, client, site, landing_page):
        """landingpage editable content should display"""
        response = client.get(landing_page.relative_url(site))
        assertContains(response, "<p>content of the landing page</p>")

    def test_tagline(self, client, site, landing_page):
        """landingpage tagline should display"""
        response = client.get(landing_page.relative_url(site))
        assertContains(response, "tagline")

    @pytest.mark.skip("todo")
    def test_header_image(self):
        pass


class TestContentPage:

    def test_visit(self, client, site, content_page):
        """contentpage should be navigable"""
        response = client.get(content_page.relative_url(site))
        assert response.status_code == 200

    def test_page_content(self, client, site, content_page):
        """contentpage editable content should display"""
        response = client.get(content_page.relative_url(site))
        assertContains(response, "<p>content of the content page</p>")


class TestPagesMenus:

    @pytest.mark.skip("todo")
    def test_child_pages_attachment(self, client):
        """
        about = Page.objects.get(title='About')
        annual_report = Page.objects.get(title='Annual Report')
        response = client.get(about.get_absolute_url())
        # page-children attachment section should be present
        assertContains(
            response, '<div class="attachments page-children">')
        # child page title and url should be present
        assertContains(response, annual_report.title)
        assertContains(response, annual_report.get_absolute_url())

        # delete child page to check behavior without
        annual_report.delete()
        response = client.get(about.get_absolute_url())
        # should not error, should not contain page-children attachment section
        assertNotContains(response, '<div class="attachments page-children">')
        """


class TestCaptionedImageBlock:

    def test_render(self):
        block = CaptionedImageBlock()
        test_img = {'url': 'kitty.png', 'width': 100, 'height': 200}
        alt_text = 'picture of a kitten'
        # NOTE: using "img" here instead of "image" means we're
        # not actually testing the image logic; but not clear how
        # to mock or use an image object in a test
        html = block.render(block.to_python({
            'img': test_img, 'alternative_text': alt_text
        }))
        assert '<figure>' in html
        assert '<img srcset="' in html
        assert 'alt="picture of a kitten" ' in html
        # no caption
        assert '<figcaption>' not in html

        # with caption
        caption = 'A kitten curled up in the sunshine'
        html = block.render(block.to_python({
            'img': test_img, 'alternative_text': alt_text,
            'caption': caption}))
        assert '<figcaption>' in html
        assert caption in html


class TestSVGImageBlock:

    def test_render(self):
        block = SVGImageBlock()
        test_svg = {'url': 'graph.svg'}  # Mock(spec=Document, url='graph.svg')
        alt_text = 'membership timeline'
        html = block.render({
            'image': test_svg, 'alternative_text': alt_text
        })
        assert ('<figure ') in html
        assert '<img role="img" ' in html
        # no caption, no extended description
        assert '<figcaption>' not in html
        assert '<div class="sr-only" ' not in html

        # with caption & extended description
        caption = 'membership activity from 1919 to 1942'
        desc = 'chart shows activity in 1920 and 1940'
        html = block.render({
            'image': test_svg, 'alternative_text': alt_text,
            'caption': caption, 'extended_description': desc})
        assert ('<figcaption>%s</figcaption' % caption) in html
        assert '<div class="sr-only" id="graphsvg-desc">' in html
        assert desc in html
