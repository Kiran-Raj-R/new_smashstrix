from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Wishlist, WishlistItem
from products.models import Product, ColorVariant
from products.utils import get_best_price, get_best_offer

@login_required(login_url="login")
def wishlist_view(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    items = wishlist.items.select_related("product","color_variant")
    for item in items:
        item.final_price = get_best_price(item.product)
        item.best_offer = get_best_offer(item.product)
    context = {"items": items}
    return render(request, "user/profile/wishlist.html", context)

@login_required(login_url="login")
def add_to_wishlist(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        variant_id = request.POST.get("variant_id")
        product = get_object_or_404(Product, id=product_id)
        color_variant = None
        if variant_id:
            color_variant = get_object_or_404(ColorVariant, id=variant_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)
        item, created = WishlistItem.objects.get_or_create(wishlist=wishlist,product=product,color_variant=color_variant)
        if created:
            messages.success(request, "Added to wishlist ❤️")
        else:
            messages.info(request, "Item already in wishlist")
    return redirect(request.META.get("HTTP_REFERER", "shop"))


@login_required(login_url="login")
def remove_from_wishlist(request, item_id):
    item = get_object_or_404(WishlistItem,id=item_id,wishlist__user=request.user)
    item.delete()
    messages.success(request, "Removed from wishlist")
    return redirect("wishlist")

