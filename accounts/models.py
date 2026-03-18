from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta

class User(AbstractUser):
    username = models.CharField(max_length=150,unique=False,blank=True,null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    pending_email = models.EmailField(null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    blocked = models.BooleanField(default=False)
    otp = models.CharField(max_length=6,null=True,blank=True)
    otp_created = models.DateTimeField(null=True,blank=True)
    otp_verified = models.BooleanField(default=False)
    mobile = models.CharField(max_length=10,unique=True,blank=True,null=True)
    profile_image = models.ImageField(upload_to="profiles/", null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def otp_expired(self):
        if not self.otp_created:
            return True
        return timezone.now() > self.otp_created + timedelta(minutes=5)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()