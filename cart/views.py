from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from products.models import Product, ColorVariant
from .models import CartItem, Cart
from .utils import get_or_create_cart
from decimal import Decimal

MAX_CART_QTY = 5

@login_required(login_url="login")
def add_to_cart(request):
    if request.method != "POST":
        return redirect("shop")

    product_id = request.POST.get("product_id")
    variant_id = request.POST.get("variant_id")
    try:
        qty = int(request.POST.get("quantity", 1))
    except (TypeError, ValueError):
        qty = 1
    if qty <= 0:
        qty = 1

    product = get_object_or_404(Product,id=product_id,active=True,brand__active=True,category__active=True)
    variant = get_object_or_404(ColorVariant,id=variant_id,product=product)
    if variant.stock <= 0:
        messages.error(request, "This product is out of stock.")
        return redirect("product_detail", slug=product.slug)

    cart = get_or_create_cart(request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart,product=product,color_variant=variant,defaults={"quantity": 0})
    new_quantity = cart_item.quantity + qty

    if new_quantity > variant.stock:
        messages.error(request, "Not enough stock available.")
        return redirect("product_detail", slug=product.slug)

    if new_quantity > MAX_CART_QTY:
        messages.error(request, f"Maximum {MAX_CART_QTY} items allowed per product.")
        return redirect("product_detail", slug=product.slug)

    cart_item.quantity = new_quantity
    cart_item.save()
    messages.success(request, "Product added to cart successfully.")
    return redirect("cart_detail")

@login_required(login_url="login")
def increment_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user)

    if not cart_item.product.active or \
       not cart_item.product.brand.active or \
       not cart_item.product.category.active:
        messages.error(request, "This product is no longer available.")
        cart_item.delete()
        return redirect("cart_detail")

    if cart_item.color_variant:
        if cart_item.quantity + 1 > cart_item.color_variant.stock:
            messages.error(request, "No more stock available.")
            return redirect("cart_detail")

    if cart_item.quantity + 1 > MAX_CART_QTY:
        messages.error(request, "Maximum quantity reached.")
        return redirect("cart_detail")
    cart_item.quantity += 1
    cart_item.save()
    return redirect("cart_detail")

@login_required(login_url="login")
def decrement_cart_item(request, item_id):
    cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    if cart_item.quantity <= 1:
        cart_item.delete()
    else:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect("cart_detail")

@login_required(login_url="login")
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem,id=item_id,cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart_detail")

@login_required(login_url="login")
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        context = {
            "cart_items": [],
            "subtotal": 0,
            "tax": 0,
            "shipping": 0,
            "grand_total": 0,
        }
        return render(request, "cart/cart_detail.html", context)
    cart_items = (cart.items.select_related("product", "color_variant").prefetch_related("product__images").all())
    subtotal = 0
    for item in cart_items:
        price = (
            item.product.discount_price
            if item.product.discount_price
            else item.product.price
        )
        item.unit_price = price
        item.total_price = price * item.quantity
        subtotal += item.total_price
    tax = subtotal * Decimal("0.05")
    shipping = 0 if subtotal > 5000 else 50
    grand_total = subtotal + tax + shipping

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "grand_total": grand_total,
    }
    return render(request, "user/profile/cart_detail.html", context)