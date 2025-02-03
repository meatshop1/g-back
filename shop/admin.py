from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline
from django import forms
from django.utils.html import format_html
from .models import Collection, Customer, Order, OrderItem, Product, ProductImage, Promotion, CartItem, Address
from django.db.models import Count
from django.core.validators import MinValueValidator

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price','inventory_status', 'collection_title', 'name_ar', 'unit']
    list_editable = ['price',]
    list_per_page = 10
    list_select_related = ['collection']
    search_fields = ['name__istartswith', 'collection__title__istartswith', 'name_ar__istartswith']

    def collection_title(self, product):
        return product.collection.title
    
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'OK'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'email', 'phone']
    search_fields = ['first_name__istartswith', 'last_name__istartswith', 'email__istartswith']
    list_select_related = ['user']
    list_per_page = 10


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']
    autocomplete_fields = ['product']
    min_num = 1
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'customer_email', 'customer_phone', 'placed_at', 'payment_status', 'address', 'customer_address', 'google_map_url']
    list_filter = ['payment_status']
    inlines = [OrderItemInline]
    date_hierarchy = 'placed_at'
    list_per_page = 10
    readonly_fields = ['customer', 'customer_email', 'customer_phone', 'placed_at', 'customer_address', 'google_map_url', 'google_map_link']

    def google_map_url(self, obj):
        print(obj.address.latitude, obj.address.longitude)
        return f'https://www.google.com/maps/search/?api=1&query={obj.address.latitude},{obj.address.longitude}' if obj.address.latitude and obj.address.longitude else None
    google_map_url.short_description = "Google Maps URL"

    def google_map_link(self, obj):
        return format_html(f'<a href="{self.google_map_url(obj)}">View on Google Maps</a>')
    google_map_link.short_description = "Google Maps Link"

    def customer_address(self, obj):
        return f'{obj.address.first_street}, {obj.address.second_street}, {obj.address.neighborhood}' if obj.address else "-"
    customer_address.short_description = "Customer Address"

    def customer_email(self, obj):
        return obj.customer.user.email if obj.customer else "-"
    customer_email.short_description = "Customer Email"

    def customer_phone(self, obj):
        return obj.customer.phone if hasattr(obj.customer, 'phone') else "-"  # Assuming a phone field exists
    customer_phone.short_description = "Customer Phone"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('customer')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count', 'title_ar']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        return collection.products_count
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count= Count('product')
        )
    

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity', 'cart']
    list_filter = ['cart']
    list_per_page = 10

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['first_street', 'second_street', 'neighborhood', 'latitude', 'longitude', 'google_map_url']
    list_per_page = 10
    readonly_fields = ['google_map_url']

    def google_map_url(self, obj):
        return f'https://www.google.com/maps/search/?api=1&query={obj.latitude},{obj.longitude}' if obj.latitude and obj.longitude else None
    google_map_url.short_description = "Google Maps URL"
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    list_filter = ['product']
    list_per_page = 10
    autocomplete_fields = ['product']

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Promotion)



