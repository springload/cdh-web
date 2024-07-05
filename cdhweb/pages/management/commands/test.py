from django.core.management.base import BaseCommand
from cdhweb.pages.models import ContentPage
from cdhweb.pages.blocks.cdh_hosted_video import HostedVideo


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Iterate through all BasePage instances
        for page in ContentPage.objects.all():
            # Access the body StreamField
            body = page.body
            # Iterate through blocks in the body
            updated_body = []
            for block in body:
                # Check if block is HostedVideo block
                if block.block_type == 'embed':
                    hosted_video_block = HostedVideo(  # Create a new HostedVideo block instance
                    video_url=block.value,
                    )
                    updated_body.append(('hosted_video', hosted_video_block))

        page.body = updated_body
        page.save()