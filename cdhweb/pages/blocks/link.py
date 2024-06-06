from wagtail import blocks


class InternalPageLinkValue(blocks.StructValue):
    @property
    def url(self):
        return self["page"].url

    @property
    def title(self):
        return self["title"] or self["page"].title


class InternalPageLinkBlock(blocks.StructBlock):
    """
    Choose a page to link your `<a href` html tag to.
    """

    page = blocks.PageChooserBlock(
        help_text="Choose a page to link to", label="Wagtail Page"
    )

    title = blocks.CharBlock(
        max_length=80,
        help_text="Set title for this link",
        label="Link title",
    )

    class Meta:
        label = "Internal Page Link"
        value_class = InternalPageLinkValue