from django.shortcuts import render
from products.models import Product

def home(request):
    return render(request,'user/home.html')
