from django.utils.cache import get_conditional_response
from django.views.generic.base import View


class LastModifiedMixin(View):
    """Mixin that adds last-modified timestamps to response for detail views.

    Uses Django's get_conditional_response to return a 304 if object has not
    been modified since time specified in the HTTP if-modified-since header.
    """

    # override to customize which attribute to use as modification date
    lastmodified_attr = "updated"

    def last_modified(self):
        """Get the last modified date of the view object."""
        return getattr(self.get_object(), self.lastmodified_attr)

    def dispatch(self, request, *args, **kwargs):
        response = super(LastModifiedMixin, self).dispatch(
            request, *args, **kwargs)

        # NOTE: remove microseconds so that comparison will pass,
        # since microseconds are not included in the last-modified header
        last_modified = self.last_modified()
        if last_modified:
            last_modified = self.last_modified().replace(microsecond=0)
            response["Last-Modified"] = last_modified.strftime(
                "%a, %d %b %Y %H:%M:%S GMT")
            last_modified = last_modified.timestamp()

        return get_conditional_response(request,
                                        last_modified=last_modified,
                                        response=response)


class LastModifiedListMixin(LastModifiedMixin):
    """Mixin that adds last-modified timestamps to response for list views.

    Uses Django's get_conditional_response to return a 304 if none of the
    objects in the list have been modified since time specified in the HTTP
    if-modified-since header.
    """

    def last_modified(self):
        """Get the most recent modification date among all view objects."""
        queryset = self.get_queryset()
        if queryset.exists():
            return getattr(
                queryset.order_by(self.lastmodified_attr).reverse().first(),
                self.lastmodified_attr)
