from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mezzanine.core.admin import DisplayableAdmin

from .models import Title, Profile, Position, Person, UserResource, ResourceType

class ProfileInline(admin.StackedInline):
    model = Profile
    max_num = 1
    # NOTE: may not be able to use displayable admin with inline;
    # could still use DisplayableAdminForm


class PositionInline(admin.TabularInline):
    model = Position


class UserResourceIinline(admin.TabularInline):
    model = UserResource

class PersonAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'current_title')
    fields = ('first_name', 'last_name', 'email')
    inlines = [ProfileInline, PositionInline, UserResourceIinline]


    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined


admin.site.register(Title)
admin.site.register(ResourceType)
admin.site.register(Person, PersonAdmin)
admin.site.register(Position)