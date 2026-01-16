from django import forms
from .models import User
import re
from django.contrib.auth import authenticate

class UserSignupForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}),label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Confirm Password'}),label='Confirm Password')

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'mobile', 'email', 'password1', 'password2']
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
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and len(password1) < 8:
            self.add_error('password1',"The password should have atleast 8 characters.")
        if password1 and password2 and password1 != password2:
            self.add_error('password2',"Passwords doesnot match.")
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserloginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder':'Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder':'Password'}))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            email = email.lower().strip()
            user = authenticate(email=email, password=password)

            if user is None:
                raise forms.ValidationError("Invalid email or password.")
            if user.blocked:
                raise forms.ValidationError("Your account has been blocked by admin.")
            if not user.is_active:
                raise forms.ValidationError("Your account is inactive.")
            cleaned_data["user"] = user

        return cleaned_data
