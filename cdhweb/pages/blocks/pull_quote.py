from wagtail import blocks


class PullQuote(blocks.StructBlock):
    class Meta:
        template = "cdhpages/blocks/pull_quote.html"
        label = "Pull Quote"
        icon = "openquote"
        group = "Body copy components"

    quote = blocks.RichTextBlock(
        features=["bold"],
        required=True,
        help_text=(
            'Pull a small section of content out as an "aside" to give it emphasis.'
        ),
        max_length=100,
    )

    attribution = blocks.RichTextBlock(
        features=["bold", "link"],
        help_text="Optional attribution",
        required=False,
        max_length=60,
    )
