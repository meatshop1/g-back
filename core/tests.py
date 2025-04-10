from django.test import TestCase

# Create your tests here.
# core/tests.py

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        """Test creating a user is successful"""
        email = 'test@example.com'
        username = 'testuser'
        password = 'testpass123'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        
    def test_create_superuser(self):
        """Test creating a superuser is successful"""
        email = 'admin@example.com'
        username = 'admin'
        password = 'adminpass123'
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        
    def test_email_is_normalized(self):
        """Test email is normalized when a user is created"""
        email = 'test@EXAMPLE.COM'
        username = 'testuser'
        password = 'testpass123'
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        self.assertEqual(user.email, email.lower())


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')
        self.login_url = reverse('jwt-create')
        
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
    def test_user_registration(self):
        """Test registering a new user is successful"""
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data['email']).exists())
        user = User.objects.get(email=self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        
    def test_user_login(self):
        """Test logging in with valid credentials"""
        # First create a user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Then attempt to login
        login_data = {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
    def test_user_login_invalid_credentials(self):
        """Test logging in with invalid credentials fails"""
        # First create a user
        user = User.objects.create_user(
            username=self.user_data['username'],
            email=self.user_data['email'],
            password=self.user_data['password']
        )
        
        # Then attempt to login with wrong password
        login_data = {
            'username': self.user_data['username'],
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_user_registration_duplicate_email(self):
        """Test registering a user with an email that already exists fails"""
        # First create a user
        user = User.objects.create_user(
            username='existinguser',
            email=self.user_data['email'],
            password='otherpass123'
        )
        
        # Then attempt to register with the same email
        response = self.client.post(self.register_url, self.user_data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthTokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_url = reverse('jwt-create')
        
    def test_auth_token_required(self):
        """Test that authentication token is required for protected endpoints"""
        # Try to access orders endpoint without authentication
        url = reverse('orders-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Login to get token
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        token = response.data['access']
        
        # Try again with authentication
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        response = self.client.get(url)
        
        # Now it should be successful (though possibly empty)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
