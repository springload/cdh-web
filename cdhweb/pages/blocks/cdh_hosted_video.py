from springkit.blocks import JumplinkableH2Block
from wagtail.blocks import CharBlock, RichTextBlock
from wagtail.embeds.blocks import EmbedBlock


class HostedVideo(JumplinkableH2Block):
    class Meta:
        template = "cdhpages/blocks/hosted_video_block.html"
        label = "CDH Hosted Video"
        icon = "media"
        group = "Images and media"

    EMBED_HELP = """This should be used for videos from Princeton's Media Central. Copy the "oEmbed URL" from the "Share" menu"""

    video_url = EmbedBlock(help_text=EMBED_HELP)

    accessibility_description = CharBlock(
        help_text="Use this to describe the video. It is used as an accessibility attribute mainly for screen readers.",
        required=True,
    )

    transcript = RichTextBlock(
        features=["bold", "link", "document-link"],
        required=False,
    )
