from django.apps import AppConfig


class PagesConfig(AppConfig):
    name = "cdhweb.pages"
    # NOTE we have to relabel this to avoid a conflict with mezzanine's pages;
    # using anything with a '.' in the name will confuse the RegexResolver and
    # result in NoReverseMatch errors when adding pages. The template directory
    # has to match this label (templates/cdhpages) for wagtail's page template
    # detection logic to work.
    label = "cdhpages"
