from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse,JsonResponse
from django.core.paginator import Paginator
from decimal import Decimal
from cart.models import Cart
from user.models import Address
from coupons.models import Coupon
from .models import Order, OrderItem
from .utils import generate_invoice
from products.utils import get_best_price
import razorpay
import json
from django.views.decorators.csrf import csrf_exempt
from wallet.models import Wallet, WalletTransaction
from decimal import Decimal

@login_required(login_url="login")
def checkout_view(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related("product","color_variant")
    except Cart.DoesNotExist:
        return redirect("cart_detail")

    if not cart_items.exists():
        return redirect("cart_detail")

    subtotal = sum((get_best_price(item.product)) * item.quantity for item in cart_items)
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
    address = get_object_or_404(Address, id=request.POST.get("address_id"), user=request.user)
    payment_method = request.POST.get("payment_method", "COD")
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related("product", "color_variant")
    except Cart.DoesNotExist:
        messages.error(request, "Cart is empty")
        return redirect("cart_detail")
    if not cart_items.exists():
        messages.error(request, "Cart is empty")
        return redirect("cart_detail")
    subtotal = sum((get_best_price(item.product)) * item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.05")
    shipping = Decimal("50.00") if subtotal < 5000 else Decimal("0.00")
    discount = Decimal("0")
    coupon = None
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            cart_total = subtotal + tax + shipping
            if coupon.valid_from <= timezone.now() <= coupon.valid_to and cart_total >= coupon.min_order_value:
                discount = (cart_total * coupon.discount_percent) / Decimal("100")
                discount = min(discount, coupon.max_discount)
        except Coupon.DoesNotExist:
            pass
    total = subtotal + tax + shipping - discount
    if payment_method == "WALLET":
        wallet = Wallet.objects.get(user=request.user)

        if wallet.balance < total:
            messages.error(request, "Insufficient wallet balance")
            return redirect("checkout")
    order = Order.objects.create(user=request.user,address=address,subtotal=subtotal,tax=tax,shipping=shipping,
        discount=discount,coupon=coupon,total=total,payment_method=payment_method,status="pending")

    for item in cart_items:
        variant = item.color_variant
        if item.quantity > variant.stock:
            messages.error(request, f"Insufficient stock for {item.product.name}")
            transaction.set_rollback(True)
            return redirect("checkout")
        variant.stock -= item.quantity
        variant.save()
        price = item.product.discount_price or item.product.price

        OrderItem.objects.create(order=order,product=item.product,color_variant=variant,
            quantity=item.quantity,price=price,total_price=price * item.quantity)
    if payment_method == "WALLET":
        wallet.balance -= total
        wallet.save()

        WalletTransaction.objects.create(user=request.user,amount=total,
            transaction_type="debit",description=f"Payment for order {order.order_id}")
        order.status = "processing"
        order.save()
    cart_items.delete()
    request.session.pop("coupon_id", None)

    return redirect("order_success", order_id=order.order_id)

@login_required(login_url="login")
def order_success(request, order_id):
    order = get_object_or_404(Order,order_id=order_id,user=request.user)
    return render(request, "orders/order_success.html", {"order": order})

@login_required(login_url="login")
def order_list(request):
    search = request.GET.get("search","")
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    if search:
        orders = orders.filter(order_id__icontains = search)
    paginator = Paginator(orders, 4)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"orders":page_obj, "search":search}
    return render(request, "orders/order_list.html", context)

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

        order.status = "cancelled"
        order.cancel_reason = reason
        order.save()
        if order.payment_method != "COD":
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            wallet.balance += order.total
            wallet.save()
            WalletTransaction.objects.create(user=request.user,amount=order.total,transaction_type="credit",
                description=f"Refund for cancelled order {order.order_id}")
            messages.success(request, "Order cancelled successfully and amount refund to wallet.")
        return redirect("order_detail", order_id=order.order_id)

    return render(request, "orders/cancel_order.html", {"order": order})

@login_required(login_url="login")
@transaction.atomic
def cancel_order_item(request, item_id):
    item = get_object_or_404(OrderItem,id=item_id,order__user=request.user)
    order = item.order
    if order.status not in ["pending", "processing"]:
        messages.error(request, "Item cannot be cancelled.")
        return redirect("order_detail", order_id=order.order_id)
    if item.status == "cancelled":
        messages.warning(request, "Item already cancelled.")
        return redirect("order_detail", order_id=order.order_id)
    if request.method == "POST":
        reason = request.POST.get("reason","")
        if item.color_variant:
            item.color_variant.stock += item.quantity
            item.color_variant.save()
        item.status = "cancelled"
        item.cancel_reason = reason
        item.save()
        if order.payment_method != "COD":
            wallet, _ = Wallet.objects.get_or_create(user=request.user)
            refund_amount = item.total_price
            wallet.balance += refund_amount
            wallet.save()
            WalletTransaction.objects.create(user=request.user,amount=refund_amount,transaction_type="credit",
                description=f"Refund for cancelled item in order {order.order_id}")
        remaining_items = order.items.filter(status="ordered").count()
        if remaining_items == 0:
            order.status = "cancelled"
            order.save()
        messages.success(request,"Item cancelled successfully.")
        return redirect("order_detail", order_id=order.order_id)
    return render(request,"orders/cancel_order_item.html",{"item":item})

@login_required(login_url="login")
def request_item_return(request, item_id):
    item = get_object_or_404(OrderItem,id=item_id,order__user=request.user)
    if item.order.status != "delivered":
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

@login_required(login_url="login")
def create_razorpay_order(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.select_related("product", "color_variant")
    except Cart.DoesNotExist:
        return JsonResponse({"error": "Cart empty"})

    if not cart_items.exists():
        return JsonResponse({"error": "Cart empty"})
    subtotal = sum(
        (get_best_price(item.product)) * item.quantity for item in cart_items)
    tax = subtotal * Decimal("0.05")
    shipping = Decimal("50.00") if subtotal < 5000 else Decimal("0.00")
    discount = Decimal("0")
    coupon_id = request.session.get("coupon_id")
    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id, is_active=True)
            total_before_discount = subtotal + tax + shipping
            if coupon.valid_from <= timezone.now() <= coupon.valid_to:
                if total_before_discount >= coupon.min_order_value:
                    discount = (total_before_discount * coupon.discount_percent) / Decimal("100")
                    if discount > coupon.max_discount:
                        discount = coupon.max_discount
        except Coupon.DoesNotExist:
            pass
    final_total = subtotal + tax + shipping - discount
    amount_in_paise = int(final_total * 100)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({"amount": amount_in_paise,"currency": "INR","payment_capture": 1})

    return JsonResponse({
        "razorpay_order_id": payment["id"],
        "amount": amount_in_paise,
        "key": settings.RAZORPAY_KEY_ID
    })

@csrf_exempt
@login_required
@transaction.atomic
def verify_payment(request):
    data = json.loads(request.body)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    try:
        client.utility.verify_payment_signature({
            "razorpay_order_id": data["razorpay_order_id"],
            "razorpay_payment_id": data["razorpay_payment_id"],
            "razorpay_signature": data["razorpay_signature"],
        })
    except:
        return JsonResponse({"success": False})
    request.POST = request.POST.copy()
    request.POST["address_id"] = data["address_id"]
    request.POST["payment_method"] = "RAZORPAY"
    response = place_order(request)
    return JsonResponse({
        "success": True,
        "redirect_url": response.url
    })

