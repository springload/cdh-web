from springkit.blocks import JumplinkableH2Block, VideoBlock


class Video(VideoBlock, JumplinkableH2Block):
    class Meta:
        template = "cdhpages/blocks/video_block.html"
        label = "Video"
        icon = "media"
        group = "Images and media"
