__version_info__ = (3, 4, 5, None)


# Dot-connect all but the last. Last is dash-connected if not None.
__version__ = ".".join([str(i) for i in __version_info__[:-1]])
if __version_info__[-1] is not None:
    __version__ += "-%s" % (__version_info__[-1],)


# context processor to add version to the template environment; can be
# manually overridden in the project's settings
def context_extras(request):
    from django.conf import settings

    return {"SW_VERSION": getattr(settings, "SW_VERSION", __version__)}
