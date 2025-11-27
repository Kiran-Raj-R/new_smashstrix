from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.db import IntegrityError
from django.db.models import Q
from accounts.models import User
from products.models import Category, Product, Brand,ProductImage, ColorVariant
from django.core.paginator import Paginator
from products.forms import BrandForm,CategoryForm,ProductForm,ProductImageForm,ColorVariantForm
from products.utils import resize_image
from PIL import Image   

def admin_login(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request,email=email,password=password)
        if user is not None and user.is_staff:
            login(request,user)
            return redirect('admin_dashboard')
        else:
            messages.error(request,"Invalid credentials or no admin access.")
    return render(request,'adminpanel/admin_login.html') 

def admin_logout(request):
    logout(request)
    return redirect('admin_login')

def admin_dashboard(request):
    context = {
        "total_users": User.objects.count(),
        "total_products": Product.objects.filter(active=True).count(),
        "total_categories": Category.objects.filter(active=True).count(),
        "total_brands": Brand.objects.filter(active=True).count(),
        "recent_users": User.objects.order_by('-date_joined')[:5],
        "recent_products": Product.objects.order_by('-created_at')[:5],
    }
    return render(request,'adminpanel/dashboard.html',context)

def admin_user_list(request):
    search = request.GET.get("search", "")

    users = User.objects.filter(email__icontains=search).exclude(email__icontains='admin').order_by("-date_joined")
    paginator = Paginator(users, 8)
    page_number = request.GET.get("page")
    users_page = paginator.get_page(page_number)

    return render(request, 'adminpanel/users/user_list.html', {"users": users_page,"search": search,})

def block_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.blocked = True
    user.save()
    messages.warning(request, f"{user.first_name} has been blocked.")
    return redirect('admin_users')

def unblock_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.blocked = False
    user.save()
    messages.success(request, f"{user.first_name} has been unblocked.")
    return redirect('admin_users')

def brand_list(request):
    search = request.GET.get('search','')
    brands = Brand.objects.filter(name__icontains=search).order_by('-created_at')

    paginator = Paginator(brands,6)
    page = request.GET.get('page')
    brands_page = paginator.get_page(page)

    context = {
        'brands':brands_page,
        'search':search,
    }

    return render(request,'adminpanel/brands/brand_list.html',context)

def brand_add(request):
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Brand added Successfully.")
            return redirect('admin_brands')
    else:
        form = BrandForm()
    
    return render(request, 'adminpanel/brands/brand_form.html', {'form':form})

def brand_edit(request,pk):
    brand = Brand.objects.get(id=pk)
    if request.method == 'POST':
        form = BrandForm(request.POST, request.FILES, instance=brand)
        if form.is_valid():
            form.save()
            messages.success(request,"Brand editted Successfully.")
            return redirect('admin_brands')
    else:
        form = BrandForm(instance=brand)
    
    return render(request,'adminpanel/brands/brand_form.html',{'form':form})

def brand_delete(request,pk):
    brand = get_object_or_404(Brand,id=pk)
    brand.active = False
    brand.save()
    messages.success(request,"Brand deleted Successfully.")
    return redirect('admin_brands')

def category_list(request):
    search = request.GET.get('search',"")
    categories = Category.objects.filter(name__icontains=search).order_by('-created_at')

    paginator = Paginator(categories,5)
    page_num = request.GET.get('page')
    page_obj = paginator.get_page(page_num)

    context = {
        'categories':page_obj,
        'search':search
    }
    return render(request,'adminpanel/categories/category_list.html',context)

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request,"Category added Successfully.")
            return redirect('admin_categories')
    else:
        form = CategoryForm()

    return render(request,'adminpanel/categories/category_form.html',{'form':form})

def category_edit(request,pk):
    category = Category.objects.get(id=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST,request.FILES,instance=category)
        if form.is_valid():
            form.save()
            messages.success(request,"Category editted Successfully.")
            return redirect('admin_categories')
    
    else:
        form = CategoryForm(instance=category)
    
    return render(request,'adminpanel/categories/category_form.html',{'form':form})

def category_delete(request,pk):
    category = Category.objects.get(id=pk)
    category.active=False
    category.save()
    messages.success(request,"Category deleted Successfully.")
    return redirect('admin_categories')

def product_add(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)        
        if form.is_valid() and image_form.is_valid():
            images = request.FILES.getlist("images")          
            if len(images) < 3:
                messages.error(request, "Upload at least 3 images.")
                return redirect("admin_product_add")
            product = form.save()
            for image in images:
                img_obj = ProductImage.objects.create(product=product, image=image)
                resize_image(img_obj.image.path)
            messages.success(request, "Product added successfully.")
            return redirect("admin_products")
    else:
        form = ProductForm()
        image_form = ProductImageForm()

    context = {
        "form": form,
        "image_form": image_form,
    }
    return render(request, "adminpanel/products/product_form.html", context)

def color_variant_add(request, product_id):
    product = Product.objects.get(id=product_id)

    if request.method == "POST":
        form = ColorVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            try:
                variant.save()
                messages.success(request, "Color variant added.")
            except IntegrityError:
                messages.error(request, "This color already exists for this product.")
            return redirect("admin_product_edit", product_id)
    else:
        form = ColorVariantForm()

    return render(request, "adminpanel/products/color_variant_form.html", {"form": form})

def color_variant_delete(request, pk):
    variant = ColorVariant.objects.get(id=pk)
    product_id = variant.product.id
    variant.delete()
    messages.success(request,"Color variant deleted.")
    return redirect("admin_product_edit", product_id)

def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        image_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            form.save()
            new_images = request.FILES.getlist("images")
            for img in new_images:
                img_obj = ProductImage.objects.create(product=product, image=img)
                resize_image(img_obj.image.path)
            messages.success(request, "Product updated successfully.")
            return redirect("admin_products")
        else:
            messages.error(request, "Please fix form errors.")
    else:
        form = ProductForm(instance=product)
        image_form = ProductImageForm()

    context = {
        "form": form,
        "image_form": image_form,
        "product": product,
        "images": product.images.all(),
        "variants": product.colors.all(),
    }
    return render(request, "adminpanel/products/product_form.html", context)

def image_resize(image_path):
    img = Image.open(image_path)
    img = img.convert("RGB")
    img = img.resize((800, 800))
    img.save(image_path)

def product_list(request):
    search = request.GET.get("search", "")
    products = Product.objects.filter(Q(name__icontains=search)|Q(brand__name__icontains=search)|
                                      Q(category__name__icontains=search),active=True).order_by("-created_at")
    paginator = Paginator(products, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "products": page_obj,
        "search": search,
    }
    return render(request, "adminpanel/products/product_list.html", context)

def product_delete(request, pk):
    product = Product.objects.get(id=pk)
    product.active = False
    product.save()

    messages.success(request, "Product removed successfully.")
    return redirect("admin_products")

def crop_center(image, crop_width, crop_height):
    width, height = image.size
    left = (width - crop_width) // 2
    top = (height - crop_height) // 2
    right = (width + crop_width) // 2
    bottom = (height + crop_height) // 2
    return image.crop((left, top, right, bottom))

def resize_image(image_path, size=(800, 800)):
    img = Image.open(image_path)
    img = img.convert("RGB")
    min_dim = min(img.size)
    img = crop_center(img, min_dim, min_dim)
    img = img.resize(size)
    img.save(image_path, optimize=True, quality=85)

def product_image_delete(request, img_id):
    img = ProductImage.objects.get(id=img_id)
    product_id = img.product.id
    img.delete()

    messages.success(request, "Image removed.")
    return redirect("admin_product_edit", product_id)

