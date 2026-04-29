from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
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
    referral_code = models.CharField(max_length=10,unique=True)
    referred_by = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)   

    def otp_expired(self):
        if not self.otp_created:
            return True
        return timezone.now() > self.otp_created + timedelta(minutes=5)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'.strip()