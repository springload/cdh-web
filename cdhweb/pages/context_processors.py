from cdhweb.pages.forms import SiteSearchForm


def site_search(request):
    """Template context processor: adds site search form to context."""
    return {"site_search": SiteSearchForm()}
