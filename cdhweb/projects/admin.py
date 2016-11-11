from django.contrib import admin

from .models import Project, GrantType, Grant, Membership, Role


admin.site.register(Project)
admin.site.register(GrantType)
admin.site.register(Grant)
admin.site.register(Role)
admin.site.register(Membership)