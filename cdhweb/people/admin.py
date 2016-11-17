from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from mezzanine.core.admin import DisplayableAdmin
from adminsortable2.admin import SortableAdminMixin

from .models import Title, Profile, Position, Person
from cdhweb.resources.models import UserResource


class TitleAdmin(SortableAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'num_people')
    # NOTE: could make title list-editable, but then we need something
    # to be the edit link
    # list_display = ('sort_order', 'title', )
    # list_editable = ('title',)

    # FIXME: there is an incompatibility with SortableAdminMixin templates
    # and/or css/js includes and grappelli; sorting works fine when
    # grappelli is not installed.  We should be able to address this
    # with a little bit of template customization.


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


admin.site.register(Title, TitleAdmin)
admin.site.register(Person, PersonAdmin)
admin.site.register(Position)