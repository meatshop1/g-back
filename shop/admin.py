from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import Collection, Customer, Order, OrderItem, Product, ProductImage, Promotion, CartItem
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
    list_display = ['id', 'placed_at', 'payment_status']
    list_filter = ['payment_status']
    inlines = [OrderItemInline]
    date_hierarchy = 'placed_at'
    list_per_page = 10

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

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']
    list_filter = ['product']
    list_per_page = 10
    autocomplete_fields = ['product']

# Register your models here.
admin.site.register(OrderItem)
admin.site.register(Promotion)



