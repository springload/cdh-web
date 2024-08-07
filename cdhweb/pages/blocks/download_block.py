from wagtail import blocks
from wagtail.documents.blocks import DocumentChooserBlock


class FileBlock(blocks.StructBlock):
    title = blocks.CharBlock(
        help_text="Title for this file as you'd like it to be seen by the public. It will fall back to document title if this field is empty",
        label="Customised File Title",
        required=False,
    )

    file = DocumentChooserBlock(
        verbose_name="Document",
        required=True,
    )


class DownloadBlock(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/download_block.html"
        label = "Download Block"
        icon = "download"
        group = "Body copy components"

    heading = blocks.CharBlock(
        required=False,
        max_length=80,
        help_text=("Heading for document block"),
    )
    description = blocks.TextBlock(
        required=False,
        max_length=150,
        help_text=(
            "A description to display with the download file (150 characters "
            "maximum)."
        ),
    )

    documents = blocks.ListBlock(
        FileBlock,
        min_num=1,
        max_num=10,
        help_text="Upload at least 1 and maximum 10 files. Each file size should be less than 5MB.",
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        documents = value.get("documents")
        file_links = []

        for document in documents:
            file = document.get("file")
            title = document.get("title")

            file_links.append(
                {
                    "title": title if title else file.title,
                    "file_size": getattr(file, "file_size", 0),
                    "file_type": getattr(file, "file_extension", "none").upper(),
                    "file": file,
                }
            )

        context["file_links"] = file_links
        return context
