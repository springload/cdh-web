# from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin

from cdhweb.projects.models import Grant, GrantType, Membership, \
    Project, ProjectRelatedLink, Role


class ResourceInline(admin.TabularInline):
    model = ProjectRelatedLink


class GrantInline(admin.TabularInline):
    model = Grant


class ProjectAdmin(DisplayableAdmin):
    # extend displayable list to add highlight and make it editable
    list_display = ("title", "status", "highlight", "admin_link", "admin_thumb",
                    "tag_list")
    list_editable = ("status", "highlight")

    list_filter = ("status", "cdh_built", "working_group",
                   "grant__grant_type", "keywords__keyword")
    # displayable date hierarchy is publish date, does that make sense here?
    date_hierarchy = "publish_date"
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('attachments', )
    search_fields = ('title', 'short_description', 'long_description',
                     'members__username', 'members__first_name',
                     'members__last_name')

    # fieldset based on displayaable admin with project fields added
    fieldsets = (
        (None, {
            "fields": ["title", "status", ("publish_date", "expiry_date"),
                       "short_description", "long_description", "highlight",
                       "cdh_built", "working_group", "image", "thumb", 'attachments'],  # tags todo
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

    inlines = [GrantInline, ResourceInline]


class GrantAdmin(admin.ModelAdmin):
    list_display = ('project', 'grant_type', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date', 'grant_type')
    date_hierarchy = 'start_date'
    search_fields = ('project__title', 'grant_type__grant_type',
                     'start_date', 'end_date', 'project__long_description',
                     'project__short_description')

    # override model ordering to show most recent first
    ordering = ['-start_date', 'project']

    def get_form(self, request, obj=None, **kwargs):
        # save object reference for filtering grants in membership Inline
        request.object = obj
        return super(GrantAdmin, self).get_form(request, obj, **kwargs)


class MembershipAdmin(admin.ModelAdmin):
    list_display = ('person', 'project', 'role', 'start_date', 'end_date')
    list_filter = ('project', 'role')
    date_hierarchy = 'start_date'
    search_fields = ('person__first_name', 'person__last_name', 'project__title')


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
