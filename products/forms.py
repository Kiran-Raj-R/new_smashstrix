from django import forms
from products.models import Brand,Category,Product,ColorVariant

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name','logo','active']
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'w-full border p-2 rounded','placeholder':'Brand Name'}),
            "active": forms.CheckboxInput(),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description','image','active']
        widgets = {
            'name':forms.TextInput(attrs={"class": "w-full border p-2 rounded",'placeholder':'Category Name'}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            'image':forms.ClearableFileInput(attrs={"class": "w-full border p-2 rounded"}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','brand','category','description','price','discount_price','active']
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "brand": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "category": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            "price": forms.NumberInput(attrs={"class": "w-full border p-2 rounded"}),
            "discounted_price": forms.NumberInput(attrs={"class": "w-full border p-2 rounded"}),
        }

class ProductImageForm(forms.Form):
    pass

class ColorVariantForm(forms.ModelForm):
    class Meta:
        model = ColorVariant
        fields = ["color", "stock"]

        widgets = {
            "color": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "stock": forms.NumberInput(attrs={"class": "w-full border p-2 rounded"}),
        }
