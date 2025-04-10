from django.test import TestCase

# Create your tests here.
# shop/tests.py

from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Collection, Product, Cart, CartItem, Address, Customer, Order, OrderItem, ProductImage
from .serializers import ProductSerializer, CollectionSerializer, CartSerializer
import uuid

User = get_user_model()


class CollectionModelTests(TestCase):
    def test_collection_creation(self):
        """Test creating a collection is successful"""
        collection = Collection.objects.create(title='Test Collection', title_ar='اختبار المجموعة')
        self.assertEqual(str(collection), 'Test Collection')
        self.assertEqual(collection.title_ar, 'اختبار المجموعة')


class ProductModelTests(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(title='Test Collection')
        
    def test_product_creation(self):
        """Test creating a product is successful"""
        product = Product.objects.create(
            name='Test Product',
            name_ar='اختبار المنتج',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection,
            unit='kilo'
        )
        
        self.assertEqual(str(product), 'Test Product')
        self.assertEqual(product.price, Decimal('99.99'))
        self.assertEqual(product.unit, 'kilo')


class CartModelTests(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        
    def test_cart_creation(self):
        """Test creating a cart is successful"""
        cart = Cart.objects.create()
        self.assertIsNotNone(cart.id)
        self.assertIsNotNone(cart.created_at)
        
    def test_cart_item_creation(self):
        """Test adding items to a cart"""
        cart = Cart.objects.create()
        cart_item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
            notes="Extra tender",
            animal="cow"
        )
        
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.product.name, 'Test Product')
        self.assertEqual(cart_item.notes, "Extra tender")
        self.assertEqual(cart_item.animal, "cow")


class AddressModelTests(TestCase):
    def test_address_creation(self):
        """Test creating an address is successful"""
        address = Address.objects.create(
            first_street='123 Main St',
            second_street='Apt 4B',
            neighborhood='Downtown',
            latitude=24.7136,
            longitude=46.6753
        )
        
        self.assertEqual(str(address), '123 Main St Apt 4B Downtown')
        self.assertEqual(address.latitude, 24.7136)
        self.assertEqual(address.longitude, 46.6753)


class OrderModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.customer = Customer.objects.create(
            user=self.user,
            phone='1234567890'
        )
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        self.address = Address.objects.create(
            first_street='123 Main St',
            second_street='Apt 4B',
            neighborhood='Downtown'
        )
        
    def test_order_creation(self):
        """Test creating an order is successful"""
        order = Order.objects.create(
            customer=self.customer,
            payment_status=Order.PAYMENT_STATUS_PENDING,
            address=self.address
        )
        
        order_item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            unit_price=self.product.price
        )
        
        self.assertEqual(order.payment_status, 'P')
        self.assertEqual(order.customer, self.customer)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.unit_price, Decimal('99.99'))


class ProductImageModelTests(TestCase):
    def setUp(self):
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        
    def test_product_image_creation(self):
        """Test creating a product image"""
        # Note: This test doesn't actually upload a file
        product_image = ProductImage.objects.create(
            product=self.product,
            image='test-image.jpg'
        )
        
        self.assertEqual(product_image.product, self.product)
        self.assertEqual(product_image.image, 'test-image.jpg')


class ProductAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
    def test_product_list(self):
        """Test retrieving a list of products"""
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_product_detail(self):
        """Test retrieving details of a product"""
        url = reverse('product-detail', args=[self.product.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
        self.assertEqual(Decimal(response.data['price']), Decimal('99.99'))
        
    def test_create_product_unauthorized(self):
        """Test creating a product without credentials fails"""
        url = reverse('product-list')
        payload = {
            'name': 'New Product',
            'description': 'New description',
            'price': '88.88',
            'inventory': 5,
            'collection': self.collection.id
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_create_product_authorized(self):
        """Test creating a product with admin credentials"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('product-list')
        payload = {
            'name': 'New Product',
            'description': 'New description',
            'price': '88.88',
            'inventory': 5,
            'collection_id': self.collection.id
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Product')


class CartAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        
    def test_create_cart(self):
        """Test creating a cart"""
        url = reverse('cart-list')
        response = self.client.post(url, {})
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        
    def test_add_cart_item(self):
        """Test adding an item to a cart"""
        # First create a cart
        cart_url = reverse('cart-list')
        cart_response = self.client.post(cart_url, {})
        cart_id = cart_response.data['id']
        
        # Then add an item to the cart
        url = reverse('cart-items-list', args=[cart_id])
        payload = {
            'product_id': self.product.id,
            'quantity': 2,
            'notes': 'Fresh cut please',
            'animal': 'cow'
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['quantity'], 2)
        
    def test_retrieve_cart(self):
        """Test retrieving a cart with items"""
        # Create a cart
        cart = Cart.objects.create()
        # Add an item to the cart
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=3
        )
        
        url = reverse('cart-detail', args=[cart.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(cart.id))
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['quantity'], 3)


class OrderAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.collection = Collection.objects.create(title='Test Collection')
        self.product = Product.objects.create(
            name='Test Product',
            description='Test description',
            price=Decimal('99.99'),
            inventory=10,
            collection=self.collection
        )
        self.address = Address.objects.create(
            first_street='123 Main St',
            second_street='Apt 4B',
            neighborhood='Downtown'
        )
        self.cart = Cart.objects.create()
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2
        )
        
    def test_create_order_authenticated(self):
        """Test creating an order when authenticated"""
        self.client.force_authenticate(user=self.user)
        url = reverse('orders-list')
        payload = {
            'cart_id': self.cart.id,
            'address_id': self.address.id
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify the order was created correctly
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer.user, self.user)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product, self.product)
        
    def test_create_order_unauthenticated(self):
        """Test creating an order when not authenticated should fail"""
        url = reverse('orders-list')
        payload = {
            'cart_id': self.cart.id,
            'address_id': self.address.id
        }
        response = self.client.post(url, payload)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 0)
