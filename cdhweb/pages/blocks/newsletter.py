from wagtail import blocks


class NewsletterBlock(blocks.StaticBlock):
    class Meta:
        template = "cdhpages/blocks/newsletter.html"
        label = "Newsletter Sign Up"
        icon = "mail"
        admin_text = "The newsletter sign up block does not require cms edit"
