from django import forms


class ProjectFiltersForm(forms.Form):
    """
    Form for validating the project filters
    """

    """
    Args:
        method/approach
        field of study
        role
        current (checkbox, defaults on)
        built by CDH (checkbox)
        q (keyword)

    """
    q = forms.CharField(required=False, label="Keyword")
    # START TODO: These need to be added as models + relations
    method = forms.ChoiceField(choices=[(None, "--Select--")])  # ??
    field = forms.ChoiceField(choices=[(None, "--Select--")])  # ??
    role = forms.ChoiceField(choices=[(None, "--Select--")])  # ??
    # END TODO
    current = forms.BooleanField(required=False, initial=True)
    cdh_built = forms.BooleanField(required=False, label="Built by CDH")
