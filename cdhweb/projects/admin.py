from django.contrib import admin

from .models import Project, GrantType, Grant, Membership, Role

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'tag_list')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'


admin.site.register(Project, ProjectAdmin)
admin.site.register(GrantType)
admin.site.register(Grant)
admin.site.register(Role)
admin.site.register(Membership)