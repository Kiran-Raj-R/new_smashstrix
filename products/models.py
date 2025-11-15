from django.db import models

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
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=50,unique=True)
    description = models.TextField()
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    discount_price = models.DecimalField(max_digits=6,decimal_places=2,null=True,blank=True)
    stock = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image = models.ImageField(upload_to='products/')

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
    