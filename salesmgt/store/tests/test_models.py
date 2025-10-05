"""
Test cases for store models (Category, Item, Delivery).
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from accounts.models import Vendor, Customer, User
from store.models import Category, Item, Delivery


class CategoryModelTest(TestCase):
    """Test cases for the Category model."""

    def setUp(self):
        """Set up test data."""
        self.category_data = {
            'name': 'Electronics'
        }

    def test_category_creation(self):
        """Test creating a new category."""
        category = Category.objects.create(**self.category_data)
        self.assertEqual(category.name, 'Electronics')
        self.assertTrue(category.slug)
        self.assertEqual(str(category), "Category: Electronics")

    def test_category_slug_generation(self):
        """Test that slug is automatically generated from name."""
        category = Category.objects.create(name='Home & Garden')
        self.assertEqual(category.slug, 'home-garden')

    def test_category_slug_uniqueness(self):
        """Test that slugs are unique."""
        Category.objects.create(name='Electronics')
        # Creating another category with the same name should generate a unique slug
        category2 = Category.objects.create(name='Electronics')
        self.assertNotEqual(category2.slug, 'electronics')

    def test_category_str_representation(self):
        """Test string representation of category."""
        category = Category.objects.create(name='Books')
        self.assertEqual(str(category), "Category: Books")

    def test_category_meta_verbose_name_plural(self):
        """Test verbose name plural."""
        self.assertEqual(Category._meta.verbose_name_plural, 'Categories')


class ItemModelTest(TestCase):
    """Test cases for the Item model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            email='vendor@example.com',
            phone='+1234567890'
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item_data = {
            'name': 'Laptop',
            'description': 'High-performance laptop',
            'category': self.category,
            'quantity': 10,
            'price': 999.99,
            'vendor': self.vendor
        }

    def test_item_creation(self):
        """Test creating a new item."""
        item = Item.objects.create(**self.item_data)
        self.assertEqual(item.name, 'Laptop')
        self.assertEqual(item.description, 'High-performance laptop')
        self.assertEqual(item.category, self.category)
        self.assertEqual(item.quantity, 10)
        self.assertEqual(item.price, 999.99)
        self.assertEqual(item.vendor, self.vendor)
        self.assertTrue(item.slug)

    def test_item_slug_generation(self):
        """Test that slug is automatically generated from name."""
        item = Item.objects.create(**self.item_data)
        self.assertEqual(item.slug, 'laptop')

    def test_item_str_representation(self):
        """Test string representation of item."""
        item = Item.objects.create(**self.item_data)
        expected_str = f"Laptop - Category: {self.category}, Quantity: 10"
        self.assertEqual(str(item), expected_str)

    def test_item_get_absolute_url(self):
        """Test get_absolute_url method."""
        item = Item.objects.create(**self.item_data)
        expected_url = f'/store/product/{item.slug}/'
        self.assertEqual(item.get_absolute_url(), expected_url)

    def test_item_to_json(self):
        """Test to_json method."""
        item = Item.objects.create(**self.item_data)
        json_data = item.to_json()
        
        self.assertEqual(json_data['id'], item.id)
        self.assertEqual(json_data['text'], 'Laptop')
        self.assertEqual(json_data['category'], 'Electronics')
        self.assertEqual(json_data['quantity'], 1)
        self.assertEqual(json_data['total_product'], 0)

    def test_item_default_values(self):
        """Test default values for quantity and price."""
        item = Item.objects.create(
            name='Test Item',
            description='Test description',
            category=self.category
        )
        self.assertEqual(item.quantity, 0)
        self.assertEqual(item.price, 0)

    def test_item_with_expiring_date(self):
        """Test item with expiring date."""
        expiry_date = timezone.now().date() + timedelta(days=30)
        item_data = self.item_data.copy()
        item_data['expiring_date'] = expiry_date
        
        item = Item.objects.create(**item_data)
        self.assertEqual(item.expiring_date, expiry_date)

    def test_item_ordering(self):
        """Test that items are ordered by name."""
        Item.objects.create(name='Zebra Product', category=self.category)
        Item.objects.create(name='Alpha Product', category=self.category)
        
        items = list(Item.objects.all())
        self.assertEqual(items[0].name, 'Alpha Product')
        self.assertEqual(items[1].name, 'Zebra Product')

    def test_item_cascade_delete_with_category(self):
        """Test that item is deleted when category is deleted."""
        item = Item.objects.create(**self.item_data)
        self.category.delete()
        
        with self.assertRaises(Item.DoesNotExist):
            Item.objects.get(id=item.id)

    def test_item_set_null_with_vendor_delete(self):
        """Test that vendor is set to null when vendor is deleted."""
        item = Item.objects.create(**self.item_data)
        self.vendor.delete()
        
        item.refresh_from_db()
        self.assertIsNone(item.vendor)


class DeliveryModelTest(TestCase):
    """Test cases for the Delivery model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
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
            description='High-performance laptop',
            category=self.category,
            quantity=10,
            price=999.99,
            vendor=self.vendor
        )
        
        self.delivery_data = {
            'item': self.item,
            'customer': self.customer,
            'date': timezone.now(),
            'is_delivered': False
        }

    def test_delivery_creation(self):
        """Test creating a new delivery."""
        delivery = Delivery.objects.create(**self.delivery_data)
        self.assertEqual(delivery.item, self.item)
        self.assertEqual(delivery.customer, self.customer)
        self.assertFalse(delivery.is_delivered)
        self.assertTrue(delivery.date)

    def test_delivery_str_representation(self):
        """Test string representation of delivery."""
        delivery = Delivery.objects.create(**self.delivery_data)
        date_str = delivery.date.strftime('%Y-%m-%d')
        expected_str = (
            f"Delivery of {self.item} to John Doe "
            f"at 123 Main St on {date_str}"
        )
        self.assertEqual(str(delivery), expected_str)

    def test_delivery_str_with_unknown_customer(self):
        """Test string representation with no customer."""
        delivery_data = self.delivery_data.copy()
        delivery_data['customer'] = None
        
        delivery = Delivery.objects.create(**delivery_data)
        date_str = delivery.date.strftime('%Y-%m-%d')
        expected_str = (
            f"Delivery of {self.item} to Unknown Customer "
            f"at Unknown Location on {date_str}"
        )
        self.assertEqual(str(delivery), expected_str)

    def test_delivery_str_with_customer_no_address(self):
        """Test string representation with customer but no address."""
        customer_no_address = Customer.objects.create(
            first_name='Jane',
            last_name='Smith',
            email='jane@example.com',
            phone='+1234567891'
        )
        
        delivery_data = self.delivery_data.copy()
        delivery_data['customer'] = customer_no_address
        
        delivery = Delivery.objects.create(**delivery_data)
        date_str = delivery.date.strftime('%Y-%m-%d')
        expected_str = (
            f"Delivery of {self.item} to Jane Smith "
            f"at Unknown Location on {date_str}"
        )
        self.assertEqual(str(delivery), expected_str)

    def test_delivery_default_is_delivered(self):
        """Test default value for is_delivered field."""
        delivery = Delivery.objects.create(
            item=self.item,
            customer=self.customer,
            date=timezone.now()
        )
        self.assertFalse(delivery.is_delivered)

    def test_delivery_set_null_with_item_delete(self):
        """Test that item is set to null when item is deleted."""
        delivery = Delivery.objects.create(**self.delivery_data)
        self.item.delete()
        
        delivery.refresh_from_db()
        self.assertIsNone(delivery.item)

    def test_delivery_cascade_delete_with_customer(self):
        """Test that delivery is deleted when customer is deleted."""
        delivery = Delivery.objects.create(**self.delivery_data)
        self.customer.delete()
        
        with self.assertRaises(Delivery.DoesNotExist):
            Delivery.objects.get(id=delivery.id)

    def test_delivery_customer_relationship(self):
        """Test the reverse relationship from customer to deliveries."""
        delivery1 = Delivery.objects.create(**self.delivery_data)
        delivery2 = Delivery.objects.create(
            item=self.item,
            customer=self.customer,
            date=timezone.now() + timedelta(days=1)
        )
        
        customer_deliveries = self.customer.deliveries.all()
        self.assertEqual(customer_deliveries.count(), 2)
        self.assertIn(delivery1, customer_deliveries)
        self.assertIn(delivery2, customer_deliveries)

    def test_delivery_nullable_fields(self):
        """Test that item and customer can be null."""
        delivery = Delivery.objects.create(
            date=timezone.now(),
            is_delivered=True
        )
        self.assertIsNone(delivery.item)
        self.assertIsNone(delivery.customer)
        self.assertTrue(delivery.is_delivered)