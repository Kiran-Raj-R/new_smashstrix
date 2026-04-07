from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponse
from django.db import transaction
from django.db.models import Q,Sum, Count
from accounts.models import User
from products.models import Category, Product, Brand,ProductImage, ColorVariant
from orders.models import Order, OrderItem
from coupons.models import Coupon
from wallet.models import Wallet, WalletTransaction
from django.core.paginator import Paginator
from products.forms import BrandForm,CategoryForm,ProductForm,ColorVariantForm
from products.utils import resize_image
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.utils import timezone
from .utils import get_filtered_orders,generate_sales_excel, generate_sales_pdf

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
    products = Product.objects.filter(Q(name__icontains=search)|Q(brand__name__icontains=search)
                                      |Q(category__name__icontains=search),).annotate(total_stock=Sum("colors__stock")).order_by("-created_at")
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

@never_cache
@login_required(login_url='admin_login')
def admin_order_list(request):
    orders = Order.objects.all().order_by("-created_at")
    search = request.GET.get("search")
    status = request.GET.get("status")
    if search:
        orders = orders.filter(Q(order_id__icontains=search) |Q(user__email__icontains=search))
    if status:
        orders = orders.filter(status=status)
    paginator = Paginator(orders, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "search": search,
        "status": status,
    }
    return render(request, "adminpanel/orders/order_list.html", context)

@never_cache
@login_required(login_url='admin_login')
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    order_items = order.items.all()
    if request.method == "POST":

        new_status = request.POST.get("status")
        if order.status in ["delivered", "cancelled"]:
            messages.error(request, "Finalized orders cannot be modified.")
            return redirect("admin_order_detail", order_id=order.order_id)

        valid_transitions = {
            "pending": ["processing", "cancelled"],
            "processing": ["shipped", "cancelled"],
            "shipped": ["out_for_delivery"],
            "out_for_delivery": ["delivered"],
        }
        allowed_statuses = valid_transitions.get(order.status, [])
        if new_status not in allowed_statuses:
            messages.error(request, "Invalid status transition.")
            return redirect("admin_order_detail", order_id=order.order_id)
        
        if new_status == "cancelled":
            for item in order_items:
                if item.color_variant:
                    item.color_variant.stock += item.quantity
                    item.color_variant.save()
            if order.payment_method != "COD":
                wallet, _ = Wallet.objects.get_or_create(user=order.user)
                wallet.balance += order.total
                wallet.save()
                WalletTransaction.objects.create(user=order.user,amount=order.total,transaction_type="credit",
                    description=f"Admin cancelled order {order.order_id}")
        order.status = new_status
        order.save()
        messages.success(request, "Order status updated successfully.")
        return redirect("admin_order_detail", order_id=order.order_id)

    context = {
        "order": order,
        "order_items": order_items,
    }
    return render(request, "adminpanel/orders/order_detail.html", context)

@never_cache
@login_required(login_url='admin_login')
def admin_return_list(request):
    status_filter = request.GET.get("status")
    if not status_filter:
        status_filter = "Requested"
    search = request.GET.get("search", "")
    return_items = OrderItem.objects.select_related(
        "order", "product", "color_variant", "order__user"
    ).exclude(return_status__isnull=True)
    if status_filter != "all":
        return_items = return_items.filter(return_status=status_filter)
    if search:
        return_items = return_items.filter(Q(order__order_id__icontains=search) |Q(product__name__icontains=search))
    return_items = return_items.order_by("-return_requested_at")
    paginator = Paginator(return_items, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "return_items": page_obj,
        "status_filter": status_filter,
        "search": search,
    }
    return render(request, "adminpanel/orders/return_list.html", context)

@never_cache
@login_required(login_url='admin_login')
@require_POST
@transaction.atomic
def admin_handle_return(request, item_id):
    action = request.POST.get("action")
    item = get_object_or_404(OrderItem, id=item_id)
    if item.return_status != "Requested":
        messages.error(request, "This return request is already processed.")
        return redirect("admin_return_list")
    if action == "approve":
        if item.color_variant:
            item.color_variant.stock += item.quantity
            item.color_variant.save()
        item.return_status = "Approved"
        item.save()
        wallet, _ = Wallet.objects.get_or_create(user=item.order.user)
        refund_amount = item.total_price
        wallet.balance += refund_amount
        wallet.save()
        WalletTransaction.objects.create(user=item.order.user,amount=refund_amount,transaction_type="credit",
            description=f"Refund for returned item in order {item.order.order_id}")
        messages.success(request, "Return approved, stock restored, and amount refunded to wallet.")
    elif action == "reject":
        item.return_status = "Rejected"
        item.save()
        messages.success(request, "Return rejected.")
    return redirect("admin_return_list")

@never_cache
@login_required(login_url='admin_login')
def coupon_list(request):
    coupons = Coupon.objects.all().order_by("-created_at")
    return render(request, "adminpanel/coupons/coupon_list.html", {"coupons": coupons})

@never_cache
@login_required(login_url='admin_login')
def add_coupon(request):
    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        discount = request.POST.get("discount")
        min_value = request.POST.get("min_order_value")
        max_discount = request.POST.get("max_discount")
        valid_from = request.POST.get("valid_from")
        valid_to = request.POST.get("valid_to")

        if not (4 <= len(code) <= 20):
            messages.error(request, "Coupon code must be 4–20 characters")
            return redirect("add_coupon")
        if " " in code:
            messages.error(request, "Coupon code should not contain spaces")
            return redirect("add_coupon")
        if Coupon.objects.filter(code=code).exists():
            messages.error(request, "Coupon already exists")
            return redirect("add_coupon")
        try:
            discount = int(discount)
            min_value = float(min_value)
            max_discount = float(max_discount)
        except:
            messages.error(request, "Invalid input values")
            return redirect("add_coupon")

        if discount <= 0 or discount > 90:
            messages.error(request, "Discount must be between 1 and 90")
            return redirect("add_coupon")

        if min_value <= 0:
            messages.error(request, "Minimum order value must be positive")
            return redirect("add_coupon")

        if max_discount <= 0:
            messages.error(request, "Max discount must be positive")
            return redirect("add_coupon")

        if valid_from >= valid_to:
            messages.error(request, "Invalid date range")
            return redirect("add_coupon")

        Coupon.objects.create(code=code,discount_percent=discount,min_order_value=min_value,max_discount=max_discount,
            valid_from=valid_from,valid_to=valid_to,is_active=True)
        messages.success(request, "Coupon added successfully")
        return redirect("coupon_list")
    return render(request, "adminpanel/coupons/add_coupon.html")

@never_cache
@login_required(login_url='admin_login')
def toggle_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    return redirect("coupon_list")

@never_cache
@login_required(login_url='admin_login')
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, "Coupon deleted")
    return redirect("coupon_list")

def sales_report(request):
    filter_type = request.GET.get("filter", "daily")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    orders = Order.objects.filter(status="delivered")
    today = timezone.now().date()
    if filter_type == "daily":
        orders = orders.filter(created_at__date=today)
    elif filter_type == "weekly":
        week_ago = today - timedelta(days=7)
        orders = orders.filter(created_at__date__gte=week_ago)
    elif filter_type == "monthly":
        orders = orders.filter(created_at__month=today.month)
    elif filter_type == "custom":
        if start_date and end_date:
            orders = orders.filter(created_at__date__range=[start_date, end_date])
    total_orders = orders.count()
    total_sales = orders.aggregate(total=Sum("total"))["total"] or 0
    total_discount = orders.aggregate(discount=Sum("discount"))["discount"] or 0
    net_revenue = total_sales

    context = {
        "orders": orders,
        "total_orders": total_orders,
        "total_sales": total_sales,
        "total_discount": total_discount,
        "net_revenue": net_revenue,
        "filter_type": filter_type,
        "start_date": start_date,
        "end_date": end_date,
    }
    return render(request, "adminpanel/reports/sales_report.html", context)

def export_sales_pdf(request):
    orders = get_filtered_orders(request)
    buffer = generate_sales_pdf(orders)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="sales_report.pdf"'
    return response

def export_sales_excel(request):
    orders = get_filtered_orders(request)
    wb = generate_sales_excel(orders)
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=sales_report.xlsx"
    wb.save(response)
    return response

