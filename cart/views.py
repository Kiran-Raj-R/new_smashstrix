from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from products.models import Product, ColorVariant
from .models import CartItem
from .utils import get_or_create_cart


@login_required(login_url="login")
def add_to_cart(request):
    if request.method != "POST":
        return redirect("shop")

    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")

    product = get_object_or_404(Product, id=product_id, active=True)

    if not product.category.active:
        messages.error(request, "This product is unavailable.")
        return redirect("shop")

    if not variant_id:
        messages.error(request, "Please select a color variant.")
        return redirect(request.META.get("HTTP_REFERER", "shop"))

    variant = get_object_or_404(ColorVariant, id=variant_id, product=product)

    if variant.stock <= 0:
        messages.error(request, "This variant is out of stock.")
        return redirect(request.META.get("HTTP_REFERER", "shop"))

    cart = get_or_create_cart(request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        color_variant=variant,
    )

    MAX_QTY = 5

    if not created:
        if cart_item.quantity + 1 > variant.stock:
            messages.error(request, "Not enough stock available.")
            return redirect(request.META.get("HTTP_REFERER", "shop"))

        if cart_item.quantity + 1 > MAX_QTY:
            messages.error(request, f"Maximum {MAX_QTY} units allowed.")
            return redirect(request.META.get("HTTP_REFERER", "shop"))

        cart_item.quantity += 1
    else:
        cart_item.quantity = 1

    cart_item.save()

    messages.success(request, "Product added to cart.")
    return redirect(request.META.get("HTTP_REFERER", "shop"))