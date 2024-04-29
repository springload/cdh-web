from cdhweb.settings import INSTALLED_APPS

# if django-dbml is installed (dev/test only), enable it
try:
    # django-dbml
    # https://github.com/makecodes/django-dbml
    import django_dbml  # noqa: F401  (do not clean up unused import)

    INSTALLED_APPS.append("django_dbml")
except ImportError:
    pass
