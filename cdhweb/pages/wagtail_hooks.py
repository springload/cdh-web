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


# Copied directly from Wagtail Recipe:
# https://docs.wagtail.io/en/stable/reference/pages/model_recipes.html#have-redirects-created-automatically-when-changing-page-slug
@hooks.register("before_edit_page")
def create_redirect_on_slug_change(request, page):
    """Automatically create a redirect when a page slug is changed."""
    if request.method == "POST":
        if page.slug != request.POST["slug"]:
            Redirect.objects.create(
                old_path=page.url[:-1],
                site=page.get_site(),
                redirect_page=page,
            )


# Adapted from Wagtail Recipe; see above
@hooks.register("before_move_page")
def create_redirect_on_move_page(request, page, destination):
    """Automatically create a redirect when a page is moved."""
    if request.method == "POST":
        Redirect.objects.create(
            old_path=page.url[:-1],
            site=page.get_site(),
            redirect_page=page,
        )
