from cdhweb.projects.models import Project, GrantType, Role
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)


class ProjectAdmin(ThumbnailMixin, ModelAdmin):
    model = Project
    menu_label = "Projects"
    menu_icon = "site"
    list_display = ("title", "admin_thumb", "live", "cdh_built", "highlight")
    list_filter = ("grants__grant_type",)
    list_export = ("title", "working_group", "cdh_built", "tags",
                   "short_description", "long_description", "website_url",
                   "updated_at")
    search_fields = ("title", "short_description", "long_description")
    export_filename = "cdhweb-projects"
    thumb_image_field_name = "thumbnail"


class GrantTypeAdmin(ModelAdmin):
    model = GrantType
    menu_icon = "pick"
    list_display = ("grant_type",)
    search_fields = ("grant_type",)


class RoleAdmin(ModelAdmin):
    model = Role
    menu_icon = "group"
    list_display = ("title", "sort_order")
    list_editable = ("title", "sort_order")
    search_fields = ("title",)


class ProjectsGroup(ModelAdminGroup):
    menu_label = "Projects"
    menu_icon = "site"
    menu_order = 210
    items = (ProjectAdmin, RoleAdmin, GrantTypeAdmin)


modeladmin_register(ProjectsGroup)
