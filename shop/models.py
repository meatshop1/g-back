from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from uuid import uuid4
from django.conf import settings
from django.contrib import admin


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
# Create your models here.

class Collection(models.Model):
    title = models.CharField(max_length=255)
    title_ar = models.CharField(max_length=255, blank=True, null=True)
    featured_product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='+', null=True, blank=True)

    def __str__(self):
        return self.title


class Product(models.Model):
    choices = [('kilo', 'Kilo'), ('quarter', 'Quarter'), ('half', 'Half'), ('full', 'Full')]
    unit = models.CharField(max_length=8, choices=choices, default='kilo')
    name = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(1, message='Price must be greater than 1')])
    inventory = models.IntegerField(validators=[MinValueValidator(0)])
    last_updated = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product-images')


class Customer(models.Model):
    phone = models.CharField(max_length=20)
    birthdate = models.DateField(null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    
    @admin.display(ordering='user__last_name') 
    def last_name(self):
        return self.user.last_name
    
    def email(self):
        return self.user.email

    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    class Meta:
        ordering = ['user__first_name', 'user__last_name']



class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    address = models.ForeignKey('Address', on_delete=models.PROTECT)
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='orderitems')
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    notes = models.TextField(blank=True, null=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)]) 
    notes = models.TextField(blank=True, null=True)
    choices = [('cow', 'Cow'), ('goat', 'Goat'), ('sheep', 'Sheep')]
    animal = models.CharField(max_length=8, choices=choices, default='cow')
    class Meta:
        unique_together = [['cart', 'product']]

class Address(models.Model):
    first_street = models.CharField(max_length=255, blank=True, null=True)
    second_street = models.CharField(max_length=255,  blank=True, null=True)
    neighborhood = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField( blank=True, null=True)
    longitude = models.FloatField( blank=True, null=True)

    def __str__(self):
        return f'{self.first_street} {self.second_street} {self.neighborhood}'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5)])
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)