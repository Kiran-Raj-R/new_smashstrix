from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.db.models import Q
from accounts.models import User
from products.models import Category, Product, Brand,ProductImage, ColorVariant
from django.core.paginator import Paginator
from products.forms import BrandForm,CategoryForm,ProductForm,ColorVariantForm
from products.utils import resize_image
from PIL import Image
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required

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

@never_cache
@login_required(login_url='admin_login')
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

@never_cache
@login_required(login_url='admin_login')
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

@never_cache
@login_required(login_url='admin_login')
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

@never_cache
@login_required(login_url='admin_login')
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
    if request.method == "POST":
        form = ProductForm(request.POST)
        images = request.FILES.getlist("images")
        print("FILES RECEIVED:", request.FILES)
        print("IMAGES LIST:", images)
        if len(images) < 3:
            return render(request, "adminpanel/products/product_form.html", {
                "form": form,
                "image_errors": "Please upload at least 3 images.",
                "product": None,
            })
        if form.is_valid():
            product = form.save()
            for img in images:
                img_obj = ProductImage.objects.create(product=product,image=img)
                resize_image(img_obj.image.path)
            messages.success(request, "Product added. Add color variants.")
            return redirect("admin_color_variant_add", product.id)
        messages.error(request, "Please fix the errors in the form.")
    else:
        form = ProductForm()
    return render(request, "adminpanel/products/product_form.html", {
        "form": form,
        "product": None,
    })

def color_variant_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ColorVariantForm(request.POST)
        if form.is_valid():
            variant = form.save(commit=False)
            variant.product = product
            variant.save()
            product.stock = sum(v.stock for v in product.colors.all())
            product.save()
            messages.success(request, "Color variant added.")
            return redirect("admin_color_variant_add", product.id)
        messages.error(request, "Please fix the errors.")
    else:
        form = ColorVariantForm()
    variants = product.colors.all()
    return render(request, "adminpanel/products/color_variant_form.html", {
        "form": form,
        "product": product,
        "variants": variants,
    })

def color_variant_delete(request, variant_id):
    variant = get_object_or_404(ColorVariant, id=variant_id)
    product = variant.product
    variant.delete()
    product.stock = sum(v.stock for v in product.colors.all())
    product.save()
    messages.success(request, "Color variant deleted.")
    return redirect("admin_color_variant_add", product.id)

def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("admin_products")
        messages.error(request, "Please fix the errors.")
    else:
        form = ProductForm(instance=product)
    images = ProductImage.objects.filter(product=product)
    return render(request, "adminpanel/products/product_form.html", {
        "form": form,
        "product": product,
        "images": images,
    })

@never_cache
@login_required(login_url='admin_login')
def product_list(request):
    search = request.GET.get("search", "")
    products = Product.objects.filter(Q(name__icontains=search)|Q(brand__name__icontains=search)|Q(category__name__icontains=search),).order_by("-created_at")
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

def product_image_delete(request, img_id):
    img = get_object_or_404(ProductImage, id=img_id)
    product_id = img.product.id
    img.delete()
    messages.success(request, "Image removed.")
    return redirect("admin_product_edit", product_id)

@never_cache
def admin_logout(request):
    logout(request)
    request.session.flush()
    return redirect('admin_login')