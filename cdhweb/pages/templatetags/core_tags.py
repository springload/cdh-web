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
    # Get footer items
    footers = Footer.objects.prefetch_related(
        "contact_links", "physical_address", "useful_links", "imprint_links"
    )

    if footers.exists():
        contact_links = footers.first().contact_links.all()
        physical_address = footers.first().physical_address.first()
        useful_links = footers.first().useful_links.all()
        imprint_links = footers.first().imprint_links.all()

        data = {
            "contact_links": contact_links,
            "physical_address": physical_address,
            "useful_links": useful_links,
            "imprint_links": imprint_links,
            "request": context["request"],
        }
        return data
    else:
        return None


def _minor_menu_item_to_dict(item):
    """
    Convert a L2 or seondary menu item to a python dictionary.
    """
    return {
        "title": item.title,
        "link_url": item.link_url,
    }


def _l1_item_to_dict(l1_item):
    """
    Convert a L1 menu item to a python dictionary.
    """
    l2_items = l1_item.l2_items.all()
    l2_item_data = [_minor_menu_item_to_dict(item) for item in l2_items]
    l1_item_data = {
        "title": l1_item.title,
        "overview": l1_item.overview,
        "section_link_title": l1_item.section_link_title,
        "link_url": l1_item.link_url,
        "l2_items": l2_item_data,
    }
    return l1_item_data


def _get_primary_nav_items():
    """
    Retrieve the primary nav items as a queryset.
    """
    l1_menu_items = []
    primary_nav = PrimaryNavigation.objects.prefetch_related(
        "l1_items", "l1_items__l2_items"
    )
    if primary_nav.exists():
        l1_menu_items = primary_nav.first().l1_items.all()
    return l1_menu_items


@register.simple_tag()
def primary_nav_dict():
    """
    Return the primary navigation data as a dict, for use with the 'json_script' filter.
    """
    primary_nav_items = _get_primary_nav_items()
    l1_menu_item_data = [_l1_item_to_dict(item) for item in primary_nav_items]

    primary_nav_data = {
        "primary_nav": {
            "l1_menu_items": l1_menu_item_data,
        },
    }

    return {"primary_nav_data": primary_nav_data}


@register.simple_tag()
def secondary_nav_dict():
    """
    Return the secondary navigation data as a dict, for use with the 'json_script' filter.
    """
    secondary_nav_items = _get_secondary_nav_items()
    cta_button = _get_secondary_nav_cta_button()
    secondary_nav_item_data = [
        _minor_menu_item_to_dict(item) for item in secondary_nav_items
    ]
    cta_button = [_minor_menu_item_to_dict(item) for item in cta_button]

    secondary_nav_data = {
        "secondary_nav": {
            "items": secondary_nav_item_data,
        },
    }

    return {"secondary_nav_data": secondary_nav_data}


def _get_secondary_nav_items():
    """
    Get secondary nav items
    """
    items = []
    secondary_nav = SecondaryNavigation.objects.prefetch_related("items")
    if secondary_nav.exists():
        items = secondary_nav.first().items.all()

    return items


def _get_secondary_nav_cta_button():
    """
    Get secondary nav cta button
    """
    secondary_nav = SecondaryNavigation.objects.prefetch_related("cta_button")

    if secondary_nav.exists():
        cta_button = secondary_nav.first().cta_button.all()
    return cta_button


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
    else:
        return None


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
    else:
        return None
