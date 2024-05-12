from wagtail import blocks


class DownloadBlock(blocks.StructBlock):
    class Meta:
        template = "core/blocks/download_block.html"
        label = "Download Block"

    # heading charfield
    # summary
    # download link - allow many within block

    ## USE SPRINGKIT