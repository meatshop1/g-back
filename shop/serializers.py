from decimal import Decimal
from rest_framework import serializers
from .models import Address, CartItem, Order, OrderItem, Product, Collection, ProductImage, Review, Cart, Customer
from django.db import transaction


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'title_ar']
    products_count = serializers.IntegerField(read_only=True)


class ProductImageSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)

    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    #if you removed required=False there's a test case will fail
    images = ProductImageSerializer(many=True, required=False)
    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'inventory', 'price_with_tax','description', 'collection', 'collection_id','images', 'name_ar', 'unit', 'collection_ar']
    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')
    collection = serializers.StringRelatedField()
    collection_id = serializers.PrimaryKeyRelatedField(queryset=Collection.objects.all(), source='collection')
    collection_ar = serializers.StringRelatedField(source='collection.title_ar')
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
    category_title = serializers.StringRelatedField(source='collection')
    category_title_ar = serializers.StringRelatedField(source='collection.title_ar')
    images = serializers.SerializerMethodField(method_name='get_images')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'unit', 'category_title', 'category_title_ar', 'name_ar', 'images']
    
    def get_images(self, product: Product):
        return [image.image.url for image in product.images.all()]



class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    class Meta:
        model = CartItem
        fields = ['id' ,'product_id', 'quantity', 'notes', 'animal']

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('Product does not exist')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        notes = self.validated_data['notes']
        animal = self.validated_data['animal']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.notes = notes
            cart_item.animal = animal
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')
    notes = serializers.CharField(allow_blank=True, required=False)

    def get_total_price(self, cart_item: CartItem):
        return cart_item.product.price * cart_item.quantity
    
    
    class Meta:
        model = CartItem
        fields = ['id' , 'product', 'quantity', 'total_price', 'notes', 'animal']



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
        fields = ['quantity', 'notes', 'animal']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    
    def save(self, **kwargs):
        self.instance.quantity = self.validated_data['quantity']
        self.instance.notes = self.validated_data['notes']
        self.instance.animal = self.validated_data['animal']
        self.instance.save()
        return self.instance
    

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
        fields = ['id', 'product', 'quantity', 'unit_price', 'notes' ]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id','first_street', 'second_street', 'neighborhood','latitude','longitude', 'google_map_url']

    google_map_url = serializers.SerializerMethodField(method_name='get_google_map_url')

    def get_google_map_url(self, address: Address):
        return f'https://www.google.com/maps/search/?api=1&query={address.latitude},{address.longitude}'
    
    def validate(self, data):
        has_address = data.get('first_street') and data.get('second_street') and data.get('neighborhood')
        has_coordinates = data.get('latitude') and data.get('longitude')

        if not has_address and not has_coordinates:
            raise serializers.ValidationError('Either address or coordinates must be provided')
        return data

    
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
                    notes = item.notes,
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            Cart.objects.filter(pk=self.validated_data['cart_id']).delete()

            return order
        

    