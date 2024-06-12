from wagtail import blocks


class NewsletterBlock(blocks.StaticBlock):
    class Meta:
        template = "includes/newsletter_form.html"
        label = "Newsletter Sign Up"
        icon = "mail"
        group = "Body copy components"
        admin_text = "The newsletter sign up block does not require cms edit"
