from decimal import Decimal
from rest_framework import serializers
from .models import Address, CartItem, Order, OrderItem, Product, Collection, ProductImage, Review, Cart, Customer
from django.db import transaction


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']
    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'inventory', 'price_with_tax','description', 'collection', 'collection_id','images']
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')
    collection = serializers.StringRelatedField()
    collection_id = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), source='collection')

    def get_price_with_tax(self, product: Product):
        return product.price * Decimal(1.1)
    

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'date', 'rating', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)
    

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']



class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id' ,'product_id', 'quantity']

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.price * cart_item.quantity
    
    
    class Meta:
        model = CartItem
        fields = ['id' , 'product', 'quantity', 'total_price']



class CartSerializer(serializers.ModelSerializer):
   id = serializers.UUIDField(read_only=True)
   items = CartItemSerializer(many=True, read_only=True)
   total_price = serializers.SerializerMethodField(method_name='get_total_price')

   def get_total_price(self, cart: Cart):
       return sum([item.product.price * item.quantity for item in cart.items.all()])
   
   class Meta:
         model = Cart
         fields = ['id', 'items', 'total_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    address_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'phone', 'birthdate', 'address_id']


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'unit_price']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','first_street', 'second_street', 'neighborhood','latitude','longitude', 'google_map_url']

    google_map_url = serializers.SerializerMethodField(method_name='get_google_map_url')

    def get_google_map_url(self, address: Address):
        return f'https://www.google.com/maps/search/?api=1&query={address.latitude},{address.longitude}'
    
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    address = AddressSerializer()
    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'customer', 'items', 'address']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    address_id = serializers.IntegerField()

    def validate_address_id(self, address_id):
        if not Address.objects.filter(pk=address_id).exists():
            raise serializers.ValidationError('Address does not exist')
        return address_id

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('Cart does not exist')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cart is empty')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            (customer, created) = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer, address_id=self.validated_data['address_id'])

            cart_items = CartItem.objects.select_related('product').filter(cart_id=self.validated_data['cart_id'])
            order_items = [
                OrderItem(
                    order = order,
                    product = item.product,
                    unit_price = item.product.price,
                    quantity = item.quantity,
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

            return order
        

    