from django.db import models
from django.conf import settings

class Brand(models.Model):
    name = models.CharField(max_length=50,unique=True)
    logo = models.ImageField(upload_to='brands/',null=True,blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=25,unique=True)
    image = models.ImageField(upload_to='categories/',blank=True,null=True)
    description = models.TextField()
    offer_percentage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=50,unique=True)
    description = models.TextField()
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=8,decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    offer_percentage = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    @property
    def thumbnail(self):
        return self.images.filter(is_primary=True).first() or self.images.first()
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/')
    is_primary = models.BooleanField(default=False)

class ColorVariant(models.Model):
    COLOR_CHOICES = [
        ('red','Red'),('blue','Blue'),('white','White'),('black','Black'),('yellow','Yellow'),('green','Green')
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE,related_name='colors')
    color = models.CharField(max_length=20,choices=COLOR_CHOICES)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('product','color')

    def __str__(self):
        return f'{self.product.name} - {self.color}'


class ProductReview(models.Model):
    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("product", "user")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.product.name} - {self.rating}★ by {self.user}"    