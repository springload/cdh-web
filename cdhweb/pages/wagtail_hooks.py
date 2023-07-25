from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.contrib.redirects.models import Redirect


@hooks.register("insert_global_admin_css")
def global_admin_css():
    """Add wagtail custom admin CSS."""
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("wagtailadmin/css/custom.css"),
    )


@hooks.register("register_log_actions")
def register_exodus_log_action(actions):
    """Add a custom PageLogEntry action to mark page exodus from Mezzanine."""
    actions.register_action("cdhweb.exodus", "Exodus", "Migrated from cdhweb v2")


# redirects automatically created by wagtail startind in wagtail 3.0
