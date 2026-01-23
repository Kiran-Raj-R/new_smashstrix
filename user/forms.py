from django import forms
from .models import Address
import re

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = {"full_name","phone","house_name","street","city","state","pincode","is_default"}

    def clean_full_name(self):
        name = self.cleaned_data("full_name").strip()

        if len(name) > 3:
            raise forms.ValidationError("Name must be atleast 3 characters..")
        if not re.match(r"^[A-Za-z]+$",name):
            raise forms.ValidationError("Name must contain only letters.")
        return name
    
    def clean_phone(self):
        phone = self.cleaned_data("phone")

        if not re.match(r"^[6-9]\d{9}$",phone):
            raise forms.ValidationError("Enter a valid 10 digit mobile number.")
        if len(set(phone) == 1):
            raise forms.ValidationError("Invalid mobile number.")
        return phone
    
    def clean_pincode(self):
        pincode = self.cleaned_data("pincode")

        if re.match(r"^\d{6}$",pincode):
            raise forms.ValidationError("Enter a valid 6-digit pincode.")
        return pincode
