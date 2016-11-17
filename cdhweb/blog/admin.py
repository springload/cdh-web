from copy import deepcopy
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from mezzanine.core.admin import (DisplayableAdmin, OwnableAdmin,
                                  BaseTranslationModelAdmin)
from mezzanine.conf import settings
from mezzanine.twitter.admin import TweetableAdminMixin

from .models import  BlogPost


# adapted from mezzanine blogpost admin

blogpost_fieldsets = deepcopy(DisplayableAdmin.fieldsets)
# blogpost_fieldsets[0][1]["fields"].insert(1, "categories")
# blogpost_fieldsets[0][1]["fields"].extend(["content", "allow_comments"])
blogpost_fieldsets[0][1]["fields"].extend(["content", "users"])
blogpost_list_display = ["title", "author_list", "status", "admin_link"]
# if settings.BLOG_USE_FEATURED_IMAGE:
blogpost_fieldsets[0][1]["fields"].insert(-2, "featured_image")
blogpost_list_display.insert(0, "admin_thumb")
blogpost_fieldsets = list(blogpost_fieldsets)
blogpost_fieldsets.insert(1, (_("Other posts"), {
    "classes": ("collapse-closed",),
    "fields": ("related_posts",)}))
# blogpost_list_filter = deepcopy(DisplayableAdmin.list_filter) + ("categories",)


class BlogPostAdmin(TweetableAdminMixin, DisplayableAdmin, OwnableAdmin):
    """
    Admin class for blog posts.
    """

    fieldsets = blogpost_fieldsets
    list_display = blogpost_list_display
    # list_filter = blogpost_list_filter
    # filter_horizontal = ("categories", "related_posts",)
    filter_horizontal = ("related_posts",)

    def save_form(self, request, form, change):
        """
        Super class ordering is important here - user must get saved first.
        """
        # OwnableAdmin.save_form(self, request, form, change)
        # NOTE: ownable automatically sets owner to current user, not
        # sure that behavior makes sense for us
        return DisplayableAdmin.save_form(self, request, form, change)


admin.site.register(BlogPost, BlogPostAdmin)
