from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin

from .models import Project, GrantType, Grant, Membership, Role, \
    ProjectResource

class MemberInline(admin.TabularInline):
    model = Membership


class ResourceInline(admin.TabularInline):
    model = ProjectResource

class GrantInline(admin.TabularInline):
    model = Grant


class ProjectAdmin(DisplayableAdmin):
    # extend displayable list to add is_active and make it editable
    list_display = ("title", "status", "is_active", "admin_link", "admin_thumb",
        "tag_list")
    list_editable = ("status", "is_active")

    list_filter = ("status", "grant", "keywords__keyword")
    # displayable date hierarchy is publish date, does that make sense here?
    date_hierarchy = "publish_date"
    prepopulated_fields = {"slug": ("title",)}

    # fieldset based on displayaable admin with project fields added
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date"),
                       "short_description", "long_description", "is_active",
                       "image", "thumb", ],  # tags todo
        }),
        ("Meta data", {
            "fields": ["_meta_title", "slug",
                       ("description", "gen_description"),
                        "keywords", "in_sitemap"],
            "classes": ("collapse-closed",)
        }),
    )

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    inlines = [GrantInline, MemberInline, ResourceInline]

class GrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'grant_type', 'start_date', 'end_date')
    date_hierarchy = 'start_date'


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'grant', 'role')


class RoleAdmin(admin.ModelAdmin):
    # TODO: drag and drop to set sort order in future
# class RoleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'sort_order')
    list_editable = ('sort_order', )


admin.site.register(Project, ProjectAdmin)
admin.site.register(GrantType)
admin.site.register(Grant, GrantAdmin)
admin.site.register(Role, RoleAdmin)
admin.site.register(Membership, MembershipAdmin)