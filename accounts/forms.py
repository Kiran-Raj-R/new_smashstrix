from django import forms
from .models import User
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email id is already registered.")
        return email
    
    def clean_mobile(self):
        mob = self.cleaned_data.get('mobile')
        if not mob.isdigit() or len(mob) not in (10,11,12):
            raise forms.ValidationError("Enter a valid mobile number")
        if User.objects.filter(mobile=mob).exists():
            raise forms.ValidationError("This mobile number is already registered.")
        return mob
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and len(password1) < 8:
            self.add_error('password1',"The password should have atleast 8 characters.")
        elif password1 and password2 and password1 != password2:
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
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(email=email,password=password)
            if not user:
                raise forms.ValidationError('Invalid email or password...')
            cleaned_data['user'] = user
        return cleaned_data
    