from django.conf import settings
from django.contrib.sites.models import Site

from cdhweb.resources.utils import absolutize_url


def template_settings(request):
    '''Template context processor: add selected setting to context
    so it can be used on any page .'''

    context_extras = {
        'SHOW_TEST_WARNING': getattr(settings, 'SHOW_TEST_WARNING', False),
        'site': Site.objects.get_current(),
        'default_preview_image': absolutize_url(''.join([settings.STATIC_URL,
                                                         'img/CDH_logo.svg']))
    }
    return context_extras