from django import forms


class SiteSearchForm(forms.Form):
    """Search form for finding pages across the site."""

    # page filter options — currently not implemented in UI
    FILTER_CHOICES = (
        ("everything", "everything"),
        ("people", "people"),
        ("updates", "updates"),
        ("projects", "projects"),
        ("events", "events"),
    )

    # keyword query
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "type": "search",
                "placeholder": "Search by keyword or phrase",
            }
        ),
    )

    # filter to different page types
    # filter = forms.ChoiceField(choices=FILTER_CHOICES)
