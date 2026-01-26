from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    address_line = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    pincode = models.CharField(max_length=6)
    country = models.CharField(max_length=50,default="India")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_default","-updated_at"]

    def __str__(self):
        return f'{self.full_name} - {self.city}'