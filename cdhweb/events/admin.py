from django.contrib import admin

from .models import EventType, Location, Event

class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_type', 'start_time', 'admin_thumb',
        'tag_list')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())
    tag_list.short_description = 'Tags'

    # use inline fields for titles and resources
    # also: suppress management/auth fields like password, username, permissions,
    # last login and date joined



admin.site.register(EventType)
admin.site.register(Location)
admin.site.register(Event, EventAdmin)

