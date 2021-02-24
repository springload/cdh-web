from pytest_django.asserts import assertContains, assertNotContains


class TestEventDetailTemplate:

    def test_event_title(self, client, workshop):
        """event detail template should include event title"""
        response = client.get(workshop.get_url())
        assertContains(response, "testing workshop")

    def test_event_content(self, client, workshop):
        """event detail template should include event content"""
        response = client.get(workshop.get_url())
        assertContains(response, "<p>my workshop description</p>", html=True)

    def test_speakers(self, client, lecture):
        """event detail template should list info for all event speakers"""
        response = client.get(lecture.get_url())
        assertContains(response, "john lecturer")           # name
        assertContains(response, "princeton university")    # affiliation

    def test_event_type(self, client, workshop):
        """event detail template should include event type"""
        response = client.get(workshop.get_url())
        assertContains(response, "<p>Workshop</p>", html=True)

    def test_event_type_name(self, client, workshop):
        """event detail template shouldn't include type if same as title"""
        workshop.title = "Workshop"
        workshop.save()
        response = client.get(workshop.get_url())
        assertNotContains(response, "<p>Workshop</p>", html=True)

    def test_when(self, client, workshop):
        """event detail template should include date/time of event"""
        response = client.get(workshop.get_url())
        assertContains(response, "<div>%s</div>" % workshop.when(), html=True)

    def test_location(self, client, workshop):
        """event detail template should include location of event"""
        response = client.get(workshop.get_url())
        assertContains(response,
                       '<span property="schema:name">Center for Digital Humanities</span>',
                       html=True)

    def test_address(self, client, workshop):
        """event detail template should include address for non-virtual event"""
        response = client.get(workshop.get_url())
        assertContains(response,
                       '<div property="schema:address">Floor B, Firestone Library</div>',
                       html=True)

    def test_address(self, client, lecture):
        """event detail template should include join url for virtual event"""
        response = client.get(lecture.get_url())
        assertContains(response, "https://princeton.zoom.us/my/zoomroom")

    def test_address(self, client, workshop):
        """event detail template should include iCal export url"""
        response = client.get(workshop.get_url())
        assertContains(response, workshop.get_ical_url())


class TestEventArchiveTemplate:
    pass
