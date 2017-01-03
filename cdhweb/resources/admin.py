from django.contrib import admin
from mezzanine.pages.admin import PageAdmin
from .models import ResourceType, Attachment, LandingPage


admin.site.register(ResourceType)
admin.site.register(Attachment)
admin.site.register(LandingPage, PageAdmin)