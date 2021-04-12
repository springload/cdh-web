from cdhweb.blog.models import BlogPost
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import ModelAdmin, modeladmin_register


class BlogPostAdmin(ThumbnailMixin, ModelAdmin):
    model = BlogPost
    menu_icon = "edit"
    list_display = ("admin_thumb", "title", "author_list",
                    "first_published_at", "live", "featured")
    list_display_add_buttons = "title"
    list_filter = ("featured", "first_published_at")
    list_export = ("title", "author_list", "first_published_at", "featured",
                   "featured_image", "tags", "body")
    export_filename = "cdhweb-blogposts"
    search_fields = ("title", "authors__person__first_name",
                     "authors__person__last_name", "body")
    exclude_from_explorer = True
    thumb_image_field_name = "featured_image"
    thumb_col_header_text = "image"
    ordering = ("-first_published_at",)
    list_per_page = 25
    menu_order = 210


modeladmin_register(BlogPostAdmin)
