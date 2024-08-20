from django.core.management.base import BaseCommand
import json
from pathlib import Path
from cdhweb.events.models import Event
from wagtail.images.models import Image


class Command(BaseCommand):
    def handle(self, *args, **options):
        """
        Update event images from the v3 version of the site

        We renamed/replaced the image fields on the Events
        for v4, but didn't make a migration to transfer the
        data -- this command populates any events that still
        have unset images to those from the latest database
        dump we have (approx 2024-04-25) -- see
        `image-mapping.json`

        Mapping prepared with
        ```
        image_mapping = {e.page_ptr_id: e.thumbnail_id for e in Event.objects.filter(thumbnail__isnull=False)}
        ```
        """
        mapping_path = Path(__file__).parent / "image-mapping.json"
        image_mapping = json.load(open(mapping_path))
        for page_id, thumbnail_id in image_mapping.items():
            if not thumbnail_id:
                continue

            event = Event.objects.filter(page_ptr_id=page_id).first()
            if not event:
                self.stderr.write(
                    f"Event page missing for page_id {page_id}",
                    style_func=self.style.WARNING,
                )
                continue

            thumbnail = Image.objects.filter(pk=thumbnail_id).first()
            if not thumbnail:
                self.stderr.write(
                    f"Image ({thumbnail_id=}) missing for page {event.title}({page_id=})",
                    style_func=self.style.WARNING,
                )
                continue

            if event.feed_image is None:
                event.feed_image = thumbnail
                self.stdout.write(
                    f"Page {event.title}({page_id=}) updated with feed image {thumbnail.title}({thumbnail_id})",
                    style_func=self.style.SUCCESS,
                )

            if event.image is None:
                event.image = thumbnail
                self.stdout.write(
                    f"Page {event.title}({page_id=}) updated with hero image {thumbnail.title}({thumbnail_id})",
                    style_func=self.style.SUCCESS,
                )

            event.save()
