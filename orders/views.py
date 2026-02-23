from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from cart.models import Cart, CartItem
from user.models import Address
from .models import Order, OrderItem

@login_required(login_url="login")
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related("product","color_variant")
    except Cart.DoesNotExist:
        return redirect("cart_detail")

    if not cart_items.exists():
        return redirect("cart_detail")

    subtotal = sum((item.product.discount_price or item.product.price) * item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.05")
    shipping = Decimal("50.00") if subtotal < 5000 else Decimal("0.00")
    total = subtotal + tax + shipping
    addresses = Address.objects.filter(user=request.user)
    default_address = addresses.filter(is_default=True).first()

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "tax": tax,
        "shipping": shipping,
        "total": total,
        "addresses": addresses,
        "default_address": default_address,
    }

    return render(request, "orders/checkout.html", context)

@login_required(login_url="login")
@transaction.atomic
def place_order(request):
    if request.method != "POST":
        return redirect("checkout")

    address_id = request.POST.get("address_id")
    address = get_object_or_404(Address, id=address_id, user=request.user)
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related("product", "color_variant")
    except Cart.DoesNotExist:
        messages.error(request, "Your cart is empty.")
        return redirect("cart_detail")

    if not cart_items.exists():
        messages.error(request, "Your cart is empty.")
        return redirect("cart_detail")

    subtotal = sum((item.product.discount_price or item.product.price) * item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.05")
    shipping = Decimal("50.00") if subtotal > 0 else Decimal("0.00")
    total = subtotal + tax + shipping
    order = Order.objects.create(user=request.user,address=address,
        subtotal=subtotal,tax=tax,shipping=shipping,
        total=total,payment_method="COD",status="pending")

    for item in cart_items:
        variant = item.color_variant
        if item.quantity > variant.stock:
            messages.error(
                request,
                f"Insufficient stock for {item.product.name}"
            )
            transaction.set_rollback(True)
            return redirect("checkout")
        variant.stock -= item.quantity
        variant.save()
        price = item.product.discount_price or item.product.price
        total_price = price * item.quantity

        OrderItem.objects.create(order=order,product=item.product,color_variant=variant,
            quantity=item.quantity,price=item.product.discount_price or item.product.price,total_price=total_price)
    cart_items.delete()

    return redirect("order_success", order_id=order.order_id)

@login_required(login_url="login")
def order_success(request, order_id):
    order = get_object_or_404(Order,order_id=order_id,user=request.user)
    return render(request, "orders/order_success.html", {"order": order})