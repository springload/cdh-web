from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Title, Profile, Position, Person

class UserProfileAdmin(UserAdmin):
    def __init__(self, *args, **kwargs):
        super(UserAdmin,self).__init__(*args, **kwargs)
        self.list_display = list(UserAdmin.list_display) + ['current_title']

    # NOTE: may actually make more sense to extend mezzanine displayable
    # admin rather than UserAdmin
    # TODO: admin fields need to be updated to include displayable fields,
    # profile fields, etc.
    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined


admin.site.register(Title)
admin.site.register(Person, UserProfileAdmin)
# admin.site.register(Profile)
admin.site.register(Position)