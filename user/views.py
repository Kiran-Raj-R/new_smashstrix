from django.shortcuts import render,redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from products.models import Product, Brand, Category, ColorVariant
from .color_map import COLOR_MAP
from django.contrib.auth.decorators import login_required
from .models import Address
from .forms import AddressForm

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

    return render(request,"user/product_detail.html",{
            "product": product,
            "related_products": related_products,
        },
    )

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request,"user/address_list.html",{'addresses':addresses})

@login_required
def address_add(request):
    initial_data = {"full_name":f"{request.user.first_name} {request.user.last_name}", "phone": {request.user.mobile}}
    form = AddressForm(request.POST or None, initial=initial_data)
    if request.method == 'POST' and form.is_valid():
        address = form.save(commit=False)
        address.user = request.user

        if address.is_default:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            address.save()
        return redirect("address_list")
    return render(request,"user/address_form.html",{'form':form})

