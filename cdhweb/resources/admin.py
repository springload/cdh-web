from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mezzanine.pages.admin import PageAdmin


from cdhweb.resources.models import ResourceType, Attachment, LandingPage

class ResourceTypeAdmin(admin.ModelAdmin):
    # TODO: drag and drop to set sort order in future
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order', )

# customize default User display
class LocalUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('is_superuser', 'is_active',
        'last_login')


admin.site.register(ResourceType, ResourceTypeAdmin)
admin.site.register(Attachment)
admin.site.register(LandingPage, PageAdmin)
# unregister and re-register User
admin.site.unregister(User)
admin.site.register(User, LocalUserAdmin)




