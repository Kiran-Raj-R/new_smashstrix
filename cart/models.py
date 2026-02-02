from django.db import models
from django.conf import settings
from products.models import Product, ColorVariant


class Cart(models.Model):
    user = models.OneToOneField( settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart of {self.user.first_name} {self.user.last_name}"

    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    def subtotal(self):
        return sum(item.item_total() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ColorVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("cart", "product", "variant")

    def __str__(self):
        return f"{self.product.name} ({self.variant.color})"

    def item_total(self):
        price = self.product.discount_price or self.product.price
        return price * self.quantity
