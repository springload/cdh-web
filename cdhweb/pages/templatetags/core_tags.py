from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from cdhweb.pages.snippets import Footer, PrimaryNavigation, SecondaryNavigation

register = template.Library()


@register.inclusion_tag("snippets/footer_menu.html", takes_context=True)
def site_footer(context):
    """
    Returns the site footer data.
    """
    # Get footer columns
    footer_columns = []
    footers = Footer.objects.prefetch_related(
        "footer_columns", "footer_columns__column_items", "imprint_links"
    )

    if footers.exists():
        footer_columns = footers.first().footer_columns.all()
        imprint_links = footers.first().imprint_links.all()

    data = {
        "footer_columns": footer_columns,
        "imprint_links": imprint_links,
        "request": context["request"],
    }
    return data


@register.inclusion_tag("snippets/primary_navigation.html", takes_context=True)
def primary_navigation(context):
    """
    Returns the primary navigation menu.
    """
    l1_menu_items = []
    main_menu = PrimaryNavigation.objects.prefetch_related(
        "l1_items", "l1_items__l2_items"
    )
    if main_menu.exists():
        l1_menu_items = main_menu.first().l1_items.all()

    data = {
        "l1_menu_items": l1_menu_items,
        "request": context["request"],
    }
    return data


@register.inclusion_tag("snippets/secondary_navigation.html", takes_context=True)
def secondary_navigation(context):
    """
    Returns the secondary navigation menu.
    """

    items = []
    secondary_menu = SecondaryNavigation.objects.prefetch_related("items", "cta_button")
    if secondary_menu.exists():
        items = secondary_menu.first().items.all()
        cta_button = secondary_menu.first().cta_button.first()

    data = {
        "secondary_nav_items": items,
        "cta_button": cta_button,
        "request": context["request"],
    }
    return data
