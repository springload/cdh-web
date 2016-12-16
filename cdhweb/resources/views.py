from django.shortcuts import render


def site_index(request):
    '''Site home page.'''
    # TODO: get random projects, upcoming events, and
    # highlighted/featured item for display
    return render(request, template_name='site_index.html')
