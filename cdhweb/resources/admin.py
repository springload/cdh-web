from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import ResourceType, Attachment, LandingPage

class ResourceTypeAdmin(admin.ModelAdmin):
    # TODO: drag and drop to set sort order in future
    list_display = ('name', 'sort_order')
    list_editable = ('sort_order', )


admin.site.register(ResourceType, ResourceTypeAdmin)
admin.site.register(Attachment)
admin.site.register(LandingPage, PageAdmin)