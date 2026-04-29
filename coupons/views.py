from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from . models import Coupon
from cart.models import CartItem
from decimal import Decimal
from products.utils import get_best_price

@login_required
def apply_coupon(request):
    code = request.POST.get("code")
    cart_items = CartItem.objects.filter(cart__user=request.user)
    if not cart_items.exists():
        return JsonResponse({"error": "Cart is empty"})
    subtotal = sum((get_best_price(item.product)) * item.quantity for item in cart_items)
    tax = subtotal * Decimal(0.05)
    shipping = Decimal("50.00") if subtotal < 5000 else Decimal("0.00")
    cart_total = subtotal + tax + shipping
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return JsonResponse({"error": "Invalid coupon"})
    if not (coupon.valid_from <= timezone.now() <= coupon.valid_to):
        return JsonResponse({"error": "Coupon expired"})
    if cart_total < coupon.min_order_value:
        return JsonResponse({
            "error": f"Minimum order ₹{coupon.min_order_value} required"
        })
    discount = (cart_total * coupon.discount_percent) / 100
    if discount > coupon.max_discount:
        discount = coupon.max_discount
    request.session["coupon_id"] = coupon.id
    request.session["discount"] = float(discount)
    request.session["final_total"] = float(cart_total - discount)

    return JsonResponse({
        "success": "Coupon applied",
        "discount": float(discount),
        "final_total": float(cart_total - discount)
    })

@login_required
def remove_coupon(request):
    request.session.pop("coupon_id", None)
    request.session.pop("discount", None)
    request.session.pop("final_total", None)
    return JsonResponse({"success": "Coupon removed"})