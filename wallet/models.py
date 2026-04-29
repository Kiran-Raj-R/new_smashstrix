from django.db import models
from django.conf import settings
import uuid

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username} Wallet - ₹{self.balance}"

class WalletTransaction(models.Model):
    TRANSACTION_TYPE = (
        ("credit", "Credit"),
        ("debit", "Debit"),
    )

    transaction_id = models.CharField(max_length=20,unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.transaction_type} - ₹{self.amount}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = f"TXN{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

