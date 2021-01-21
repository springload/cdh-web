from cdhweb.projects.models import Project, GrantType, Role
from wagtail.contrib.modeladmin.mixins import ThumbnailMixin
from wagtail.contrib.modeladmin.options import (ModelAdmin, ModelAdminGroup,
                                                modeladmin_register)


class ProjectAdmin(ThumbnailMixin, ModelAdmin):
    model = Project
    menu_label = "Projects"
    menu_icon = "site"
    list_display = ("title", "live", "highlight", "admin_thumb", "tags")
    list_editable = ("live", "highlight")
    list_filter = ("live", "cdh_built", "working_group")
    list_export = ("title", "working_group", "cdh_built", "tags",
                   "short_description", "long_description", "website_url",
                   "updated_at")
    search_fields = ("title", "short_description", "grant__grant_type")


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


# TODO inlines for editing ProjectRelatedLinks (#181) on Project
modeladmin_register(ProjectsGroup)
