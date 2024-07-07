from django.conf import settings
from wagtail.models import Site
from django.conf.urls.static import static

from cdhweb.pages.utils import absolutize_url


def template_settings(request):
    """Template context processor: add selected setting to context
    so it can be used on any page ."""

    feature_flags = getattr(settings, "FEATURE_FLAGS", [])

    #  default social preview image, relative to static url
    if "purple-mode" in feature_flags:
        default_preview_img = "img/alt-modes/purple/cdhlogo_square.png"
    else:
        default_preview_img = "images/cdhlogo_square.jpg"

    context_extras = {
        "SHOW_TEST_WARNING": getattr(settings, "SHOW_TEST_WARNING", False),
        "site": Site.find_for_request(request),
        "default_preview_image": request.build_absolute_uri(
            static(default_preview_img)
        ),
        # try using template tag import static tag and use here instead of join django utils static
        # Include analytics based on settings.DEBUG or override in settings.py
        # Defaults to opposite of settings.DEBUG
        "INCLUDE_ANALYTICS": getattr(settings, "INCLUDE_ANALYTICS", not settings.DEBUG),
        "GTAGS_ANALYTICS_ID": getattr(
            settings, "GTAGS_ANALYTICS_ID", not settings.DEBUG
        ),
        # pass any feature flags that are configured
        "FEATURE_FLAGS": feature_flags,
        "FAVICON": favicon_path(),
    }
    return context_extras


def favicon_path():
    """Determine which favicon to use based on any feature flags and test warning.
    Returns full local path, including static url.
    """
    feature_flags = getattr(settings, "FEATURE_FLAGS", [])

    base_path = ""
    if "purple-mode" in feature_flags:
        base_path = "img/alt-modes/purple/"

    icon_version = "favicon.ico"
    # use test favicon when test warning is enabled as another visual indicator
    if getattr(settings, "SHOW_TEST_WARNING", False):
        icon_version = "favicon-test.ico"

    return "".join([settings.STATIC_URL, base_path, icon_version])


def show_test_warning(request):
    return {"SHOW_TEST_WARNING": getattr(settings, "SHOW_TEST_WARNING", False)}
