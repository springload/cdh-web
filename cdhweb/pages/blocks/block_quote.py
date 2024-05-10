from wagtail import blocks


class BlockQuote(blocks.StructBlock):
    class Meta:
        template = "core/blocks/block_quote.html"
        label = "Block Quote"

    # quote - textfield - Add and style a longer form quotation to make it stand out from the rest of your text. Used if a quote is longer than 40 words. 