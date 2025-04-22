from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from cdhweb.pages.snippets import (
    Footer,
    PrimaryNavigation,
    SecondaryNavigation,
    SiteAlert,
)

register = template.Library()


@register.inclusion_tag("snippets/footer_menu.html", takes_context=True)
def site_footer(context):
    """
    Returns the site footer data.
    """
    # Get footer items
    footer = Footer.objects.prefetch_related(
        "contact_links", "useful_links", "imprint_links"
    ).first()

    data = {
        "request": context["request"],
        "site_search": context["site_search"],
        "SW_VERSION": context["SW_VERSION"],
    }
    if footer:
        contact_links = footer.contact_links.all()
        social_media_links = footer.social_media_links.all()
        physical_address = footer.address
        useful_links = footer.useful_links.all()
        imprint_links = footer.imprint_links.all()

        data |= {
            "contact_links": contact_links,
            "social_media_links": social_media_links,
            "physical_address": physical_address,
            "useful_links": useful_links,
            "imprint_links": imprint_links,
        }
    return data


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
    ).first()
    if primary_nav:
        l1_menu_items = primary_nav.l1_items.all()
    return l1_menu_items


@register.simple_tag(takes_context=True)
def primary_nav_dict(context):
    """
    Return the primary navigation data as a dict, for use with the 'json_script' filter.
    """
    primary_nav_items = _get_primary_nav_items()
    l1_menu_item_data = [_l1_item_to_dict(item) for item in primary_nav_items]

    current_path = context["request"].path

    for item in l1_menu_item_data:
        if current_path.startswith(item["link_url"]):
            item["is_current"] = True
        else:
            item["is_current"] = False

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
        "secondary_nav": {"items": secondary_nav_item_data, "cta": cta_button},
    }

    return {"secondary_nav_data": secondary_nav_data}


def _get_secondary_nav_items():
    """
    Get secondary nav items
    """
    items = []
    secondary_nav = SecondaryNavigation.objects.prefetch_related("items").first()
    if secondary_nav:
        items = secondary_nav.items.all()

    return items


def _get_secondary_nav_cta_button():
    """
    Get secondary nav cta button
    """
    secondary_nav = SecondaryNavigation.objects.prefetch_related("cta_button").first()

    if secondary_nav:
        return secondary_nav.cta_button.all()
    return []


@register.simple_tag()
def primary_navigation():
    """
    Returns the primary navigation menu.
    """
    l1_menu_items = []
    main_menu = PrimaryNavigation.objects.prefetch_related(
        "l1_items", "l1_items__l2_items"
    ).first()
    if main_menu:
        l1_menu_items = main_menu.l1_items.all()

        data = {
            "l1_menu_items": l1_menu_items,
        }
        return data
    else:
        return None


@register.simple_tag()
def secondary_navigation():
    """
    Returns the secondary navigation menu.
    """

    items = []
    secondary_menu = SecondaryNavigation.objects.prefetch_related(
        "items", "cta_button"
    ).first()
    if secondary_menu:
        items = secondary_menu.items.all()
        cta_button = secondary_menu.cta_button.first()

        data = {
            "secondary_nav_items": items,
            "cta_button": cta_button,
        }

        return data
    else:
        return None


@register.inclusion_tag("includes/site_alert.html", takes_context=True)
def site_alerts(context):
    now = timezone.now()
    site_alerts = (
        SiteAlert.objects.all()
        .exclude(display_from__gt=now)
        .exclude(display_until__lt=now)
    )
    data = {"site_alerts": site_alerts, "request": context.get("request")}
    return data


@register.filter
def starts_with(value, arg):
    """
    Usage, {% if value|starts_with:"arg" %}
    """
    if value:
        return value.startswith(arg)
    return None
