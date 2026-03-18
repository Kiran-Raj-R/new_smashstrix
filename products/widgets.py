from django import forms

class MultiFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

    def __init__(self, attrs=None):
        attrs = attrs or {}
        attrs["multiple"] = True
        super().__init__(attrs)