from django import forms

from cdhweb.projects.models import ProjectField, ProjectMethod, ProjectRole


class ProjectFiltersForm(forms.Form):
    """
    Form for validating the project filters
    """

    q = forms.CharField(required=False, label="Keyword")
    method = forms.ModelChoiceField(
        ProjectMethod.objects.all(),
        empty_label="--Select--",
        required=False,
        blank=True,
    )
    field = forms.ModelChoiceField(
        ProjectField.objects.all(),
        empty_label="--Select--",
        required=False,
        blank=True,
    )
    role = forms.ModelChoiceField(
        ProjectRole.objects.all(),
        empty_label="--Select--",
        required=False,
        blank=True,
    )
    current = forms.BooleanField(required=False, initial=True)
    cdh_built = forms.BooleanField(required=False, label="Built by CDH")
