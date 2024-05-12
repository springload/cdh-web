from wagtail import blocks


class AccordionGroup(blocks.StructBlock):
    class Meta:
        template = "core/blocks/accordion_group.html"
        label = "Accordion Group"
    
    # heading - short heading for group of accordions - 

    # summary - description introducing and giving context to group of accordions - textfield

    # accordion:
        # heading - short heading for accordion. Ideal: 45 characters (max 80 characters) - charfield - required
        # summary - short summary to describe accordion contents. Only add if it is needed. (max 85 chars) - textfield
        # body - rich text field - required