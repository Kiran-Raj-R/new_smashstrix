from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator
from products.models import Product, Brand, Category, ColorVariant
from .color_map import COLOR_MAP
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from .models import Address
from .forms import AddressForm, EditProfileForm, ChangePasswordForm
from django.contrib import messages
from accounts.utils import send_email_change_otp


def home(request):
    return render(request, "user/home.html")

def shop(request):
    products = Product.objects.filter(active=True)
    q = request.GET.get("q")
    if q:
        products = products.filter(name__icontains=q)
    selected_categories = request.GET.getlist("category")
    if selected_categories:
        products = products.filter(category_id__in=selected_categories)
    selected_brands = request.GET.getlist("brand")
    if selected_brands:
        products = products.filter(brand_id__in=selected_brands)
    selected_colors = request.GET.getlist("color")
    if selected_colors:
        products = products.filter(colors__color__in=selected_colors).distinct()

    min_price = request.GET.get("min")
    max_price = request.GET.get("max")

    if min_price == "0" and max_price == "0":
        min_price = None
        max_price = None
    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort = request.GET.get("sort")
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")
    elif sort == "az":
        products = products.order_by("name")
    elif sort == "za":
        products = products.order_by("-name")
    else:
        products = products.order_by("-created_at")

    paginator = Paginator(products, 6)
    page = request.GET.get("page")
    products = paginator.get_page(page)

    query_params = request.GET.copy()
    if "page" in query_params:
        del query_params["page"]
    querystring = query_params.urlencode()

    context = {
        "products": products,
        "querystring": querystring,
        "brands": Brand.objects.filter(active=True),
        "categories": Category.objects.filter(active=True),
        "colors": ColorVariant.objects.values_list("color", flat=True).distinct(),
        "COLOR_MAP": COLOR_MAP,
        "selected_brands": selected_brands,
        "selected_categories": selected_categories,
        "selected_colors": selected_colors,
        "min_price": min_price,
        "max_price": max_price,
        "request": request,
    }

    return render(request, "user/shop.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, active=True)
    related_products = Product.objects.filter(category=product.category, active=True).exclude(id=product.id)[:4]
    return render(request,"user/product_detail.html",{"product": product,"related_products": related_products,},)

@login_required(login_url="login")
def user_profile(request):
    default_address = (
        Address.objects.filter(user=request.user, is_default=True).first())
    return render(request, "user/profile/profile.html", {"default_address": default_address})

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request,"user/address_list.html",{'addresses':addresses})

@login_required
def address_add(request):
    initial_data = {"full_name":f"{request.user.first_name} {request.user.last_name}", "phone": {request.user.mobile}, "country":"India"}
    form = AddressForm(request.POST or None, initial=initial_data)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user
        if not Address.objects.filter(user=request.user).exists():
            address.is_default = True
        elif address.is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
        return redirect("address_list")
    return render(request,"user/address_form.html",{'form':form, 'mode':'add'})

@login_required
def address_edit(request,pk):
    address = get_object_or_404(Address, pk=pk, user = request.user)
    form = AddressForm(request.POST or None, instance=address)
    if request.method == 'POST' and form.is_valid():
        updated_address = form.save(commit=False)
        if updated_address.is_default:
            Address.objects.filter(user=request.user,is_default=True).exclude(pk=pk).update(is_default=False)
            updated_address.save()
        return redirect("address_list")
    return render(request,"user/address_form.html",{'form':form,'mode':'edit'})

@login_required
def address_delete(request,pk):
    address = get_object_or_404(Address,pk=pk,user=request.user)
    if request.method == 'POST':
        is_default = address.is_default
        address.delete()
        if is_default:
            new_default = Address.objects.filter(User=request.user).first()
            if new_default:
                new_default.is_default=True
                new_default.save()
    return redirect("address_list")

@login_required
def address_set_default(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
    address.is_default = True
    address.save()
    return redirect("address_list")

@login_required
def edit_profile(request):
    user = request.user
    old_email = user.email
    form = EditProfileForm(request.POST or None, instance=user)
    if request.method == "POST" and form.is_valid():
        new_email = form.cleaned_data["email"]
        user.first_name = form.cleaned_data["first_name"]
        user.last_name = form.cleaned_data["last_name"]
        user.mobile = form.cleaned_data["mobile"]

        if new_email != old_email:
            send_email_change_otp(user, new_email)
            messages.info(request, "OTP sent to your new email for verification.")
            return redirect("verify_email_change")
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("profile")
    return render(request, "user/profile/edit_profile.html", {"form": form})

@login_required
def verify_email_change(request):
    user = request.user
    if request.method == "POST":
        otp = request.POST.get("otp")
        if user.otp == otp and not user.otp_expired():
            user.email = user.pending_email
            user.pending_email = None
            user.otp = None
            user.otp_created = None
            user.otp_verified = True
            user.save()
            messages.success(request, "Email updated successfully.")
            return redirect("profile")
        messages.error(request, "Invalid or expired OTP.")
    return render(request, "user/profile/verify_email.html")

@login_required
def change_password(request):
    form = ChangePasswordForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = request.user
        old_password = form.cleaned_data["old_password"]
        new_password = form.cleaned_data["new_password"]

        if not user.check_password(old_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("change_password")
        user.set_password(new_password)
        user.save()
        logout(request)

        messages.success(request, "Password changed successfully. Please login again.")
        return redirect("login")
    return render(request, "user/profile/change_password.html", {"form": form})