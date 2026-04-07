from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, WalletTransaction
import razorpay
from django.conf import settings
from django.http import JsonResponse
from decimal import Decimal
import json
from django.views.decorators.csrf import csrf_exempt

@login_required(login_url="login")
def wallet_detail(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    transactions = WalletTransaction.objects.filter(user=request.user).order_by("-created_at")
    context = {
        "wallet": wallet,
        "transactions": transactions
    }

    return render(request, "wallet/wallet_detail.html", context)

@login_required(login_url="login")
def create_wallet_order(request):
    amount = Decimal(request.GET.get("amount"))
    if amount <= 0:
        return JsonResponse({"error": "Invalid amount"})
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment = client.order.create({"amount": int(amount * 100),"currency": "INR","payment_capture": 1})

    return JsonResponse({"order_id": payment["id"],"amount": int(amount * 100),"key": settings.RAZORPAY_KEY_ID})

@csrf_exempt
@login_required(login_url="login")
def verify_wallet_payment(request):
    data = json.loads(request.body)
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    try:
        client.utility.verify_payment_signature(data)
    except:
        return JsonResponse({"success": False})
    amount = Decimal(data["amount"])
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    wallet.balance += amount
    wallet.save()

    WalletTransaction.objects.create(user=request.user,amount=amount,transaction_type="credit",description="Wallet top-up")
    
    return JsonResponse({"success": True})