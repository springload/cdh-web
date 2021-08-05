from django.urls import reverse

from cdhweb.projects.views import ProjectListView


class MyProjectListView(ProjectListView):
    """Project list view subclass for testing"""

    page_title = "My Projects"
    past_title = "My Past Projects"


class TestProjectListView:
    def test_page_titles(self, rf, projects):
        """should be able to customize section titles"""
        request = rf.get("/projects/my")
        view = MyProjectListView()
        view.setup(request)
        view.dispatch(request)
        view.get_queryset()
        context = view.get_context_data(request=request)
        assert context["page_title"] == "My Projects"
        assert context["past_title"] == "My Past Projects"

    def test_archive_nav_urls(self, rf, projects):
        """should output archive nav with urls"""
        request = rf.get("/projects/my")
        view = MyProjectListView()
        view.setup(request)
        view.dispatch(request)
        view.get_queryset()
        context = view.get_context_data(request=request)
        nav_urls = [x[1] for x in context["archive_nav_urls"]]
        assert reverse("projects:sponsored") in nav_urls
        assert reverse("projects:staff") in nav_urls
        assert reverse("projects:working-groups") in nav_urls

    def test_get_queryset(self, rf, projects):
        """should get all published projects, ordered by newest grant"""
        request = rf.get("/projects/my")
        view = MyProjectListView()
        view.setup(request)
        view.dispatch(request)
        qs = view.get_queryset()

        # should be ordered by newest grant
        assert qs[0] == projects["derrida"]  # RPG started 1yr ago
        assert qs[1] == projects["pliny"]  # started 400 days ago
        assert qs[2] == projects["ocampo"]  # started 450 days ago
        assert qs[3] == projects["slavic"]  # seed grant 2yrs ago

    def test_get_current(self, rf, projects):
        """should get current projects"""
        # get queryset
        request = rf.get("/projects/my")
        view = MyProjectListView()
        view.setup(request)
        view.dispatch(request)
        view.get_queryset()
        qs = view.get_current()

        # slavic working group grant ended so it is "past"
        assert projects["derrida"] in qs
        assert projects["pliny"] in qs
        assert projects["ocampo"] in qs
        assert projects["slavic"] not in qs

    def test_get_past(self, rf, projects):
        """should get past projects"""
        # get queryset
        request = rf.get("/projects/my")
        view = MyProjectListView()
        view.setup(request)
        view.dispatch(request)
        view.get_queryset()
        qs = view.get_past()

        # slavic working group grant ended so it is "past"
        assert projects["slavic"] in qs
        assert projects["derrida"] not in qs
        assert projects["pliny"] not in qs
        assert projects["ocampo"] not in qs
