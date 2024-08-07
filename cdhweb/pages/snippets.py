from django.core.exceptions import ValidationError
from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet


class Level2MenuItem(Orderable, ClusterableModel):
    """
    Represents a 'second-level' menu item.
    """

    title = models.CharField(max_length=60, verbose_name="Item title")
    link = StreamField(
        [
            ("page", blocks.PageChooserBlock()),
            ("external", blocks.URLBlock()),
        ],
        use_json_field=True,
        max_num=1,
    )

    l1_parent = ParentalKey(
        "Level1MenuItem", related_name="l2_items", on_delete=models.CASCADE
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("link"),
    ]

    @property
    def link_url(self):
        """This saves a bit of faff in the templates."""
        if not self.link[0].value:
            return None
        if self.link[0].block_type == "page":
            return self.link[0].value.url
        return self.link[0].value

    def __str__(self):
        return self.title


class Level1MenuItem(Orderable, ClusterableModel):
    """
    Represents a 'first-level' menu item.
    """

    main_menu = ParentalKey(
        "PrimaryNavigation", related_name="l1_items", on_delete=models.CASCADE
    )

    title = models.CharField(
        max_length=60,
        verbose_name="Menu item title",
        blank=False,
        null=False,
    )
    overview = models.TextField(
        verbose_name="Section overview",
        max_length=120,
        blank=True,
        null=False,
    )
    section_link = StreamField(
        [
            ("page", blocks.PageChooserBlock()),
            ("external", blocks.URLBlock()),
        ],
        use_json_field=True,
        max_num=1,
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("overview"),
        FieldPanel("section_link"),
        InlinePanel("l2_items", label="Second-level menu items", max_num=20),
    ]

    @property
    def link_url(self):
        """This saves a bit of faff in the templates."""
        if not self.section_link[0].value:
            return None
        if self.section_link[0].block_type == "page":
            return self.section_link[0].value.url
        return self.section_link[0].value

    def __str__(self):
        return self.title


@register_snippet
class PrimaryNavigation(ClusterableModel):
    """
    Root element of the menu.
    """

    def __str__(self):
        return f"Primary Navigation #{self.pk}"

    class Meta:
        verbose_name = "Primary Navigation"
        verbose_name_plural = "Primary Navigation"

    panels = [
        InlinePanel("l1_items", label="Top-level menu items", max_num=7),
    ]

    def clean(self):
        # Singleton implemented here rather than as a mixin so that we can
        # customise the error message below.
        model = self.__class__
        if model.objects.count() > 0 and self.pk != model.objects.get().pk:
            raise ValidationError(
                "Only one Main Menu allowed. Please go back and edit the existing one."
            )
        super().clean()


class MiniMenuItemBase(Orderable, ClusterableModel):
    class Meta:
        abstract = True

    title = models.CharField(max_length=60, verbose_name="link title")
    link = StreamField(
        [
            ("page", blocks.PageChooserBlock()),
            ("external", blocks.URLBlock()),
        ],
        use_json_field=True,
        max_num=1,
    )
    panels = [
        FieldPanel("title"),
        FieldPanel("link"),
    ]

    @property
    def link_url(self):
        """This saves a bit of faff in the templates."""
        if not self.link[0].value:
            return None
        if self.link[0].block_type == "page":
            return self.link[0].value.url
        return self.link[0].value

    def __str__(self):
        return f"Mini menu item: {self.title}"


class MiniMenu(ClusterableModel):
    class Meta:
        verbose_name = "Mini Menu"
        verbose_name_plural = "Mini Menu"
        abstract = True

    def __str__(self):
        return f"Mini Menu #{self.pk}"

    def clean(self):
        # Singleton implemented here rather than as a mixin so that we can
        # customise the error message below.
        model = self.__class__
        if model.objects.count() > 0 and self.pk != model.objects.get().pk:
            verbose_name = self._meta.verbose_name
            raise ValidationError(
                f"Only one {verbose_name} allowed. Please go back and edit the existing one."
            )
        super().clean()


class SecondaryNavigationItem(MiniMenuItemBase):
    secondary_menu = ParentalKey(
        "SecondaryNavigation", related_name="items", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Secondary navigation item: {self.title}"


class SecondaryNavigationCTAButton(MiniMenuItemBase):
    secondary_menu = ParentalKey(
        "SecondaryNavigation", related_name="cta_button", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Secondary navigation item: {self.title}"


@register_snippet
class SecondaryNavigation(MiniMenu):
    """
    Root element of the secondary navigation.
    """

    def __str__(self):
        return f"Secondary navigation #{self.pk}"

    class Meta:
        verbose_name = "Secondary Navigation"
        verbose_name_plural = "Secondary Navigation"

    panels = [
        InlinePanel("items", label="Secondary navigation items", max_num=3),
        InlinePanel("cta_button", label="Secondary navigation cta button", max_num=1),
    ]


@register_snippet
class Footer(ClusterableModel):
    """
    A Snippet for the site's footer that includes two columns.
    """

    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footer"

    address = RichTextField(features=["bold"], verbose_name="Physical Address")

    panels = [
        InlinePanel("contact_links", label="Contact Links", min_num=1),
        InlinePanel("social_media_links", label="Social Media Links", max_num=6),
        FieldPanel("address"),
        InlinePanel("useful_links", label="Useful links", min_num=1),
        InlinePanel("imprint_links", label="Imprint links", max_num=4),
    ]

    def __str__(self):
        return "Site Footer"

    def clean(self):
        # Singleton implemented here rather than as a mixin etc, so that we can
        # customise the error message below.
        model = self.__class__
        if model.objects.count() > 0 and self.pk != model.objects.get().pk:
            raise ValidationError(
                "Only one Footer allowed. Please go back and edit the existing one."
            )
        super().clean()


class ImprintLinkItem(MiniMenuItemBase):
    """
    Imprint link item for the bottom of the footer.
    Consists of a title and link to internal or external page.
    """

    imprint_link = ParentalKey(
        "Footer", related_name="imprint_links", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Imprint link item: {self.title}"


class UsefulLinksItem(MiniMenuItemBase):
    """
    Useful link item for the second column of the footer.
    Consists of a title and link to internal or external page.
    """

    contact_link = ParentalKey(
        "Footer", related_name="useful_links", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Useful link item: {self.title}"


class ContactLinksItem(models.Model):
    """
    Contact link item for the first column of the footer.
    Consists of a title and link to internal or external page.
    """

    contact_link = ParentalKey(
        "Footer", related_name="contact_links", on_delete=models.CASCADE
    )

    body = RichTextField(features=["bold", "link"])

    panels = [
        FieldPanel("body"),
    ]


class SocialMediaLinks(models.Model):
    class SocialChoices(models.TextChoices):
        BLUESKY = "bluesky", "Bluesky"
        TWITTER = "twitter", "Twitter"
        LINKEDIN = "linkedIn", "LinkedIn"
        INSTAGRAM = "instagram", "Instagram"
        FACEBOOK = "facebook", "Facebook"
        GITHUB = "github", "Github"

    social_media_link = ParentalKey(
        "Footer", related_name="social_media_links", on_delete=models.CASCADE
    )

    site = models.CharField(
        choices=SocialChoices.choices,
    )
    url = models.URLField(null=False, blank=False)

    panels = [
        FieldPanel("site"),
        FieldPanel("url"),
    ]


class AlertTypeChoices(models.TextChoices):
    ALERT_WARNING = "warning", "Warning"
    ALERT_INFO = "info", "Info"
    ALERT_EMERGENCY = "emergency", "Emergency"


@register_snippet
class SiteAlert(models.Model):
    title = models.CharField(max_length=80, blank=True)
    message = RichTextField(features=["bold", "italic", "link"])
    alert_type = models.CharField(
        choices=AlertTypeChoices.choices, default=AlertTypeChoices.ALERT_INFO
    )
    display_from = models.DateTimeField(blank=True, null=True)
    display_until = models.DateTimeField(blank=True, null=True)
    dismissable = models.BooleanField(default=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("message"),
        FieldPanel("alert_type"),
        FieldPanel("display_from"),
        FieldPanel("display_until"),
        FieldPanel("dismissable"),
    ]

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f"Alert {self.id}"

    def clean(self):
        """
        Add some custom validation.
        """
        errors = {}
        if self.display_from and self.display_until:
            # Make sure the dates are in the right order
            if self.display_from > self.display_until:
                inverted_date_message = "Display from date is after display until date. Are the dates in the wrong order?"
                errors["display_from"] = inverted_date_message
                errors["display_until"] = inverted_date_message

        if errors:
            raise ValidationError(errors)

        return super().clean()

    @property
    def alert_id(self):
        return f"alert_{self.id}"
