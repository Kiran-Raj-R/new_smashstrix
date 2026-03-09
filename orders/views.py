from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
from decimal import Decimal
from cart.models import Cart, CartItem
from user.models import Address
from .models import Order, OrderItem
from .utils import generate_invoice

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
    shipping = Decimal("50.00") if subtotal < 5000 else Decimal("0.00")
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

@login_required(login_url="login")
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "orders/order_list.html", {"orders": orders})

@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = OrderItem.objects.filter(order=order)

    context = {
        "order": order,
        "order_items": order_items
    }
    return render(request, "orders/order_detail.html", context)

@login_required(login_url="login")
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)
    order_items = order.items.all()
    buffer = generate_invoice(order, order_items)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order.order_id}.pdf'
    return response

@login_required(login_url="login")
@transaction.atomic
def cancel_order(request, order_id):
    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    if order.status not in ["pending", "processing"]:
        messages.error(request, "This order cannot be cancelled.")
        return redirect("order_detail", order_id=order.order_id)
    if request.method == "POST":
        reason = request.POST.get("reason", "")
        for item in order.items.all():
            if item.color_variant:
                item.color_variant.stock += item.quantity
                item.color_variant.save()
            else:
                item.product.stock += item.quantity
                item.product.save()

        order.status = "Cancelled"
        order.cancel_reason = reason
        order.save()
        messages.success(request, "Order cancelled successfully.")
        return redirect("order_detail", order_id=order.order_id)

    return render(request, "orders/cancel_order.html", {"order": order})

@login_required
def request_item_return(request, item_id):
    item = get_object_or_404(OrderItem,id=item_id,order__user=request.user)
    if item.order.status != "Delivered":
        messages.error(request, "Return allowed only for delivered items.")
        return redirect("order_detail", order_id=item.order.order_id)
    if item.return_status != "Not Requested":
        messages.error(request, "Return already requested for this item.")
        return redirect("order_detail", order_id=item.order.order_id)
    if request.method == "POST":
        reason = request.POST.get("reason")
        if not reason:
            messages.error(request, "Return reason is required.")
            return redirect("request_item_return", item_id=item.id)

        item.return_status = "Requested"
        item.return_reason = reason
        item.return_requested_at = timezone.now()
        item.save()
        messages.success(request, "Return request submitted.")
        return redirect("order_detail", order_id=item.order.order_id)
    return render(request, "orders/request_item_return.html", {"item": item})