from django import forms
from .models import Address
from accounts.models import User
import re

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = {"full_name","phone","address_line","city","state","pincode","country","is_default"}

    widgets = {"full_name": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder": "Full Name"}),
            "phone": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder": "Mobile Number"}),
            "address_line": forms.Textarea(attrs={"class": "w-full border p-2 rounded","rows": 3,"placeholder": "House no, Street, Landmark"}),
            "city": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "state": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "pincode": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "country": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
        }

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

class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "mobile"]
        widgets = {
            'first_name' : forms.TextInput(attrs={'placeholder':'First name'}),
            'last_name' : forms.TextInput(attrs={'placeholder':'Last Name'}),
            'mobile' : forms.TextInput(attrs={'placeholder':'Mob. No'}),
            'email' : forms.EmailInput(attrs={'placeholder':'Email'}),
        }

    def clean_first_name(self):
        name = self.cleaned_data.get("first_name","").strip()
        if len(name) < 3:
            raise forms.ValidationError("First name must be atleast 3 characters long.")
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise forms.ValidationError("Names should not contain only specical characters or numbers.")
        return name.capitalize()
    
    def clean_last_name(self):
        name = self.cleaned_data.get("last_name","").strip()
        if not re.fullmatch(r"[A-Za-z]+", name):
            raise forms.ValidationError("Names should not contain only specical characters or numbers.")
        return name.capitalize()
    

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email id is already registered.")
        return email
    
    def clean_mobile(self):
        mob = self.cleaned_data.get('mobile',"").strip()
        if not re.fullmatch(r"\d{10}",mob):
            raise forms.ValidationError("Mobile number must contain exactly 10 numbers.")
        if len(set(mob))==1:
            raise forms.ValidationError("Enter a valid mobile number")
        if mob[0] not in "6789":
            raise forms.ValidationError("Enter a valid Indian number.")
        if User.objects.filter(mobile=mob).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mob