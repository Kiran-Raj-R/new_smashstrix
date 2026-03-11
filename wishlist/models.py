from django.db import models
from django.conf import settings
from products.models import Product, ColorVariant

class Wishlist(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s Wishlist"

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    color_variant = models.ForeignKey(ColorVariant,on_delete=models.CASCADE,null=True,blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("wishlist", "product", "color_variant")

    def __str__(self):
        return f"{self.product.name}"