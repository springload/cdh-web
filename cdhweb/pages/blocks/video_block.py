from springkit.blocks import HeadingBlock, VideoBlock
from springkit.blocks.jumplinks import JumplinkMixin


class Video(JumplinkMixin, VideoBlock):
    heading = HeadingBlock(required=False)

    class Meta:
        template = "cdhpages/blocks/video_block.html"
        label = "Video"
        icon = "media"
        group = "Images and media"
