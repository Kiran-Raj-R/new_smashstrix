from django.db import models
from django.conf import settings
from django.utils import timezone
from products.models import Product, ColorVariant
from user.models import Address
import uuid

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("shipped", "Shipped"),
        ("out_for_delivery", "Out For Delivery"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_CHOICES = [
        ("COD", "Cash on Delivery"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="orders")
    order_id = models.CharField(max_length=20,unique=True,editable=False)
    address = models.ForeignKey(Address,on_delete=models.SET_NULL,null=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")
    payment_method = models.CharField(max_length=20,choices=PAYMENT_CHOICES,default="COD")
    created_at = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        if not self.order_id:
            self.order_id = "SMX" + uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_id

class OrderItem(models.Model):

    STATUS_CHOICES = [
        ("ordered", "Ordered"),
        ("cancelled", "Cancelled"),
        ("returned", "Returned"),
    ]

    order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name="items")
    product = models.ForeignKey(Product,on_delete=models.SET_NULL,null=True)
    color_variant = models.ForeignKey(ColorVariant,on_delete=models.SET_NULL,null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="ordered")
    cancel_reason = models.TextField(blank=True, null=True)
    return_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} ({self.order.order_id})"