from django import forms
from products.models import Brand,Category,Product,ColorVariant
from django.core.exceptions import ValidationError
from .widgets import MultiFileInput

ALLOWED_EXTENSIONS = ["jpg","jpeg","webp","png"]
ALLOWED_CONTENT_TYPES = ["image/jpeg","image/webp","image/png","image/PNG"]

def validate_image(file):
    ext = file.name.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError("Only jpg,jpeg,png and webp images are allowed.")
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError("Invalid file format.")
    
    return file

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name','logo','active']
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'w-full border p-2 rounded','placeholder':'Brand Name'}),
            'logo': forms.FileInput(attrs={'accept':'image/*'}),
            "active": forms.CheckboxInput(),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description','image','active']
        widgets = {
            'name':forms.TextInput(attrs={"class": "w-full border p-2 rounded",'placeholder':'Category Name'}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            'image':forms.ClearableFileInput(attrs={"class": "w-full border p-2 rounded",'accept':'image/*'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','brand','category','price','discount_price','description','active']
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "brand": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "category": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            "price": forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min":1}),
            "discount_price": forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min":0}),
            "active": forms.CheckboxInput(attrs={"class":"h-4 w-4"}),
        }
    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greated than zero.")
        return price
    
    def clean_discount_price(self):
        discount = self.cleaned_data.get("discount_price")
        price = self.cleaned_data.get("price")
        if discount is not None and discount < 0:
            raise forms.ValidationError("Discount price cannot be negative.")
        if discount and price and discount >= price:
            raise forms.ValidationError("Discount cannot be greater than the price.")
        return discount

class ColorVariantForm(forms.ModelForm):
    class Meta:
        model = ColorVariant
        fields = ["color", "stock"]

        widgets = {
            "color": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "stock": forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min":0}),
        }
    def clean_stock(self):
        stock = self.cleaned_data.get("stock")
        if stock is not None and stock < 0:
            raise forms.ValidationError("Stock cannot be negative number.")
        return stock