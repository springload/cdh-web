from wagtail import blocks


class BlockQuote(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/block_quote.html"
        label = "Block Quote"
        icon = "openquote"
        group = "Body copy components"

    quote = blocks.RichTextBlock(
        features=["bold"],
        required=True,
        help_text=(
            "Add and style a longer form quotation to make it stand out from the rest of your text. Used if a quote is longer than 40 words"
        ),
    )
