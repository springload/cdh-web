from wagtail.embeds.blocks import EmbedBlock


class EmbedBlock(EmbedBlock):
    class Meta:
        icon = "warning"
        group = "Deprecated"

    def __init__(self, *args, **kwargs):
        kwargs[
            "help_text"
        ] = """This block exists to help with data migration. It will be deleted when content loading is complete.
                         Please use the CDH Hosted Video instead. """
        super().__init__(*args, **kwargs)
