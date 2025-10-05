"""
Test cases for store views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import JsonResponse
from unittest.mock import patch
import json

from accounts.models import Vendor, Customer, Profile, UserRole
from store.models import Category, Item, Delivery
from store.views import dashboard, normalize_data
from sales.models import Sale, SaleDetail, Purchase

User = get_user_model()


class DashboardViewTest(TestCase):
    """Test cases for the dashboard view."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create profile for the user
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )
        
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            email='vendor@example.com',
            phone='+1234567890'
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Laptop',
            description='Test laptop',
            category=self.category,
            quantity=10,
            price=999.99,
            vendor=self.vendor
        )

    def test_dashboard_requires_login(self):
        """Test that dashboard requires user to be logged in."""
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/accounts/login/?next=/store/')

    def test_dashboard_with_authenticated_user(self):
        """Test dashboard view with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Store Analytics Dashboard')

    def test_dashboard_context_data(self):
        """Test that dashboard provides correct context data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        context = response.context
        self.assertIn('items_count', context)
        self.assertIn('profiles_count', context)
        self.assertIn('total_items', context)
        self.assertIn('top_items_labels', context)
        self.assertIn('top_items_quantities', context)

    def test_dashboard_with_no_data(self):
        """Test dashboard with no sales/purchase data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        
        self.assertEqual(response.status_code, 200)
        # Should handle empty data gracefully


class NormalizeDataFunctionTest(TestCase):
    """Test cases for the normalize_data helper function."""

    def test_normalize_empty_list(self):
        """Test normalizing empty list."""
        result = normalize_data([])
        self.assertEqual(result, [])

    def test_normalize_single_value(self):
        """Test normalizing single value."""
        result = normalize_data([50])
        self.assertEqual(result, [100])

    def test_normalize_multiple_values(self):
        """Test normalizing multiple values."""
        result = normalize_data([10, 20, 30, 40, 50])
        expected = [20, 40, 60, 80, 100]
        self.assertEqual(result, expected)

    def test_normalize_with_zero_max(self):
        """Test normalizing when max value is zero."""
        result = normalize_data([0, 0, 0])
        self.assertEqual(result, [0, 0, 0])

    def test_normalize_with_none_values(self):
        """Test normalizing with None values."""
        result = normalize_data([10, None, 30])
        expected = [33, 0, 100]
        self.assertEqual(result, expected)

    def test_normalize_with_floats(self):
        """Test normalizing with float values."""
        result = normalize_data([1.5, 3.0, 4.5])
        expected = [33, 67, 100]
        self.assertEqual(result, expected)


class ItemViewTest(TestCase):
    """Test cases for Item-related views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )
        
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            email='vendor@example.com',
            phone='+1234567890'
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Test Laptop',
            description='A test laptop',
            category=self.category,
            quantity=10,
            price=999.99,
            vendor=self.vendor
        )

    def test_product_list_view(self):
        """Test product list view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')

    def test_product_detail_view(self):
        """Test product detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('product-detail', kwargs={'slug': self.item.slug})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Laptop')
        self.assertContains(response, 'A test laptop')

    def test_product_create_view_get(self):
        """Test GET request to product create view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('product-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Product')

    def test_product_create_view_post_valid(self):
        """Test POST request to product create view with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'name': 'New Product',
            'description': 'A new test product',
            'category': self.category.id,
            'quantity': 5,
            'price': 499.99,
            'vendor': self.vendor.id
        }
        
        response = self.client.post(reverse('product-create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check that the product was created
        self.assertTrue(
            Item.objects.filter(name='New Product').exists()
        )

    def test_product_update_view(self):
        """Test product update view."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'name': 'Updated Laptop',
            'description': 'An updated test laptop',
            'category': self.category.id,
            'quantity': 15,
            'price': 1099.99,
            'vendor': self.vendor.id
        }
        
        response = self.client.post(
            reverse('product-update', kwargs={'slug': self.item.slug}),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the product was updated
        self.item.refresh_from_db()
        self.assertEqual(self.item.name, 'Updated Laptop')
        self.assertEqual(self.item.quantity, 15)

    def test_product_delete_view(self):
        """Test product delete view."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('product-delete', kwargs={'slug': self.item.slug})
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the product was deleted
        self.assertFalse(
            Item.objects.filter(id=self.item.id).exists()
        )


class CategoryViewTest(TestCase):
    """Test cases for Category-related views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )
        
        self.category = Category.objects.create(name='Electronics')

    def test_category_list_view(self):
        """Test category list view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('category-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electronics')

    def test_category_detail_view(self):
        """Test category detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('category-detail', kwargs={'pk': self.category.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Electronics')

    def test_category_create_view_post_valid(self):
        """Test POST request to category create view with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {'name': 'Books'}
        
        response = self.client.post(reverse('category-create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # Check that the category was created
        self.assertTrue(
            Category.objects.filter(name='Books').exists()
        )

    def test_category_update_view(self):
        """Test category update view."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {'name': 'Updated Electronics'}
        
        response = self.client.post(
            reverse('category-update', kwargs={'pk': self.category.pk}),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the category was updated
        self.category.refresh_from_db()
        self.assertEqual(self.category.name, 'Updated Electronics')

    def test_category_delete_view(self):
        """Test category delete view."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('category-delete', kwargs={'pk': self.category.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the category was deleted
        self.assertFalse(
            Category.objects.filter(id=self.category.id).exists()
        )


class DeliveryViewTest(TestCase):
    """Test cases for Delivery-related views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )
        
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890',
            address='123 Main St'
        )
        
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            email='vendor@example.com',
            phone='+1234567890'
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Laptop',
            description='Test laptop',
            category=self.category,
            quantity=10,
            price=999.99,
            vendor=self.vendor
        )
        
        self.delivery = Delivery.objects.create(
            item=self.item,
            customer=self.customer,
            date=timezone.now(),
            is_delivered=False
        )

    def test_delivery_list_view(self):
        """Test delivery list view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('deliveries'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Laptop')

    def test_delivery_create_view_get(self):
        """Test GET request to delivery create view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('delivery-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Delivery')

    def test_delivery_create_with_existing_customer(self):
        """Test creating delivery with existing customer."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'item': self.item.id,
            'existing_customer': self.customer.id,
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        response = self.client.post(reverse('delivery-create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        
        # Check that delivery count increased
        self.assertEqual(Delivery.objects.count(), 2)

    def test_delivery_update_view(self):
        """Test delivery update view."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'item': self.item.id,
            'existing_customer': self.customer.id,
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': True  # Update delivery status
        }
        
        response = self.client.post(
            reverse('delivery-update', kwargs={'pk': self.delivery.pk}),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the delivery was updated
        self.delivery.refresh_from_db()
        self.assertTrue(self.delivery.is_delivered)

    def test_delivery_delete_view(self):
        """Test delivery delete view."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('delivery-delete', kwargs={'pk': self.delivery.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the delivery was deleted
        self.assertFalse(
            Delivery.objects.filter(id=self.delivery.id).exists()
        )


class PermissionTestMixin:
    """Mixin for testing view permissions."""

    def test_view_requires_login(self):
        """Test that view requires authentication."""
        if hasattr(self, 'url'):
            response = self.client.get(self.url)
            self.assertRedirects(
                response, 
                f'/accounts/login/?next={self.url}'
            )

    def test_view_with_authenticated_user(self):
        """Test view with authenticated user."""
        if hasattr(self, 'url'):
            self.client.login(username='testuser', password='testpass123')
            response = self.client.get(self.url)
            self.assertIn(response.status_code, [200, 302])  # Allow redirects


class ViewPermissionTest(TestCase, PermissionTestMixin):
    """Test permissions for various views."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.profile = Profile.objects.create(
            user=self.user,
            role=UserRole.ADMIN
        )

    def test_dashboard_permission(self):
        """Test dashboard view permission."""
        self.url = reverse('dashboard')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()

    def test_product_list_permission(self):
        """Test product list view permission."""
        self.url = reverse('product-list')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()

    def test_category_list_permission(self):
        """Test category list view permission."""
        self.url = reverse('category-list')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()