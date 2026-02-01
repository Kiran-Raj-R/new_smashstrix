from django import forms
from .models import Address
from accounts.models import User
import re

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ["full_name","phone","address_line","city","state","pincode","is_default"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder": "Full Name"}),
            "phone": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder": "Mobile Number"}),
            "address_line": forms.Textarea(attrs={"class": "w-full border p-2 rounded","rows": 3,"placeholder": "House no, Street, Landmark"}),
            "city": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder":"City"}),
            "state": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder":"State"}),
            "pincode": forms.TextInput(attrs={"class": "w-full border p-2 rounded","placeholder":"Pincode"}),
            "is_default": forms.CheckboxInput(attrs={"class":"h-4 w-4"}),
        }

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name","").strip()
        if len(name) < 3:
            raise forms.ValidationError("Name must be atleast 3 characters..")
        if not re.fullmatch(r"^[A-Za-z ]+",name):
            raise forms.ValidationError("Name must contain only letters.")
        return name
    
    def clean_phone(self):
        phone = self.cleaned_data.get("phone","").strip()

        if not re.fullmatch(r"^[6-9]\d{9}$",phone):
            raise forms.ValidationError("Enter a valid 10 digit mobile number.")
        if len(set(phone)) == 1:
            raise forms.ValidationError("Invalid mobile number.")
        return phone
    
    def clean_pincode(self):
        pincode = self.cleaned_data.get("pincode","").strip()

        if not re.fullmatch(r"^[1-9]\d{5}$",pincode):
            raise forms.ValidationError("Enter a valid 6-digit pincode.")
        return pincode

class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "mobile"]
        widgets = {
            'first_name' : forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2 text-sm",'placeholder':'First name'}),
            'last_name' : forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2 text-sm",'placeholder':'Last Name'}),
            'mobile' : forms.TextInput(attrs={"class": "w-full border rounded px-3 py-2 text-sm",'placeholder':'Mob. No'}),
            'email' : forms.EmailInput(attrs={"class": "w-full border rounded px-3 py-2 text-sm",'placeholder':'Email'}),
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
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
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
        if User.objects.filter(mobile=mob).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mob
    
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Current Password"}),label="Current Password")
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "New Password"}),label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Confirm New Password"}),label="Confirm New Password")

    def clean(self):
        cleaned_data = super().clean()
        new = cleaned_data.get("new_password")
        confirm = cleaned_data.get("confirm_password")
        if new and len(new) < 8:
            raise forms.ValidationError("New password must be at least 8 characters.")
        if new != confirm:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data