from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import JsonResponse
from . models import Coupon

@login_required
def apply_coupon(request):
    code = request.POST.get("code")
    cart_total = request.session.get("grand_total", 0)
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
    new_total = cart_total - discount

    request.session["coupon_id"] = coupon.id
    request.session["discount"] = float(discount)
    request.session["final_total"] = float(new_total)
    return JsonResponse({
        "success": "Coupon applied",
        "discount": float(discount),
        "final_total": float(new_total)
    })

@login_required
def remove_coupon(request):
    request.session.pop("coupon_id", None)
    request.session.pop("discount", None)
    request.session.pop("final_total", None)

    return JsonResponse({"success": "Coupon removed"})

