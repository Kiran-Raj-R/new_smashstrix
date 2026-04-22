from django import forms
from products.models import Brand,Category,Product,ColorVariant
from django.core.exceptions import ValidationError

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
    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Brand name is required.")
        qs = Brand.objects.exclude(id=self.instance.id).filter(name__iexact=name)
        if qs.exists():
            raise forms.ValidationError("Brand already exists.")
        return name.title()

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name','description','image','offer_percentage','active']
        widgets = {
            'name':forms.TextInput(attrs={"class": "w-full border p-2 rounded",'placeholder':'Category Name'}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            'image':forms.ClearableFileInput(attrs={"class": "w-full border p-2 rounded",'accept':'image/*'}),
            'offer_percentage': forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min": 0,"max": 100,"placeholder": "Offer %"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Category name is required.")
        qs = Category.objects.exclude(id=self.instance.id).filter(name__iexact=name)
        if qs.exists():
            raise forms.ValidationError("Category already exists.")
        return name.title()

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','brand','category','price','offer_percentage','description','active']
        widgets = {
            "name": forms.TextInput(attrs={"class": "w-full border p-2 rounded"}),
            "brand": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "category": forms.Select(attrs={"class": "w-full border p-2 rounded"}),
            "description": forms.Textarea(attrs={"class": "w-full border p-2 rounded"}),
            "price": forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min":1}),
            "offer_percentage": forms.NumberInput(attrs={"class": "w-full border p-2 rounded","min": 0,"max": 100,"placeholder": "Offer %"}),
            "active": forms.CheckboxInput(attrs={"class":"h-4 w-4"}),
        }

    def clean_name(self):
        name = self.cleaned_data.get("name", "").strip()
        if not name:
            raise forms.ValidationError("Product name is required.")
        qs = Product.objects.exclude(id=self.instance.id).filter(name__iexact=name)
        if qs.exists():
            raise forms.ValidationError("Product already exists.")
        return name.title()

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greated than zero.")
        return price

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