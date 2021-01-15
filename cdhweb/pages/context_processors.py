from cdhweb.pages.models import PageIntro


def page_intro(request):
    '''Template context processor: if there is a PageIntro snippet
    for this page, add it to the context for display.'''
    # wagtail stores link url without leading and trailing slashes,
    # but requests to django view urls include them; strip them off to match
    page_intro = PageIntro.objects.filter(
        page__link_url=request.path.strip('/')).first()
    if page_intro:
        return {'page_intro': page_intro}
    return {}
