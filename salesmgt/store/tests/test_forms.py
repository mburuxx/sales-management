"""
Test cases for store forms (ItemForm, CategoryForm, DeliveryForm).
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from accounts.models import Vendor, Customer, User
from store.models import Category, Item
from store.forms import ItemForm, CategoryForm, DeliveryForm


class ItemFormTest(TestCase):
    """Test cases for the ItemForm."""

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
        
        self.valid_form_data = {
            'name': 'Test Laptop',
            'description': 'A high-performance laptop for testing',
            'category': self.category.id,
            'quantity': 5,
            'price': 999.99,
            'vendor': self.vendor.id
        }

    def test_valid_item_form(self):
        """Test form with valid data."""
        form = ItemForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_item_form_save(self):
        """Test saving a valid form."""
        form = ItemForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        
        item = form.save()
        self.assertEqual(item.name, 'Test Laptop')
        self.assertEqual(item.quantity, 5)
        self.assertEqual(item.price, 999.99)

    def test_quantity_validation_negative(self):
        """Test quantity validation with negative value."""
        form_data = self.valid_form_data.copy()
        form_data['quantity'] = -5
        
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)
        self.assertIn('The quantity must be 1 or greater.', form.errors['quantity'])

    def test_quantity_validation_zero(self):
        """Test quantity validation with zero value."""
        form_data = self.valid_form_data.copy()
        form_data['quantity'] = 0
        
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_price_validation_negative(self):
        """Test price validation with negative value."""
        form_data = self.valid_form_data.copy()
        form_data['price'] = -100.00
        
        form = ItemForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)
        self.assertIn('The price cannot be negative.', form.errors['price'])

    def test_price_validation_zero(self):
        """Test price validation with zero value (should be valid)."""
        form_data = self.valid_form_data.copy()
        form_data['price'] = 0.00
        
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_required_fields(self):
        """Test that required fields are validated."""
        form = ItemForm(data={})
        self.assertFalse(form.is_valid())
        
        required_fields = ['name', 'description', 'category', 'quantity', 'price']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_form_with_expiring_date(self):
        """Test form with expiring date."""
        form_data = self.valid_form_data.copy()
        form_data['expiring_date'] = timezone.now().date() + timedelta(days=30)
        
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_without_vendor(self):
        """Test form without vendor (should be valid)."""
        form_data = self.valid_form_data.copy()
        del form_data['vendor']
        
        form = ItemForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_widget_classes(self):
        """Test that form widgets have correct CSS classes."""
        form = ItemForm()
        
        self.assertEqual(form.fields['name'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['category'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['quantity'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['price'].widget.attrs['class'], 'form-control')


class CategoryFormTest(TestCase):
    """Test cases for the CategoryForm."""

    def test_valid_category_form(self):
        """Test form with valid data."""
        form_data = {'name': 'Electronics'}
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_category_form_save(self):
        """Test saving a valid form."""
        form_data = {'name': 'Books & Media'}
        form = CategoryForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        category = form.save()
        self.assertEqual(category.name, 'Books & Media')

    def test_empty_name_validation(self):
        """Test validation with empty name."""
        form_data = {'name': ''}
        form = CategoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_required_name_field(self):
        """Test that name field is required."""
        form = CategoryForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_form_widget_attributes(self):
        """Test that form widget has correct attributes."""
        form = CategoryForm()
        
        widget_attrs = form.fields['name'].widget.attrs
        self.assertEqual(widget_attrs['class'], 'form-control')
        self.assertEqual(widget_attrs['placeholder'], 'Enter category name')
        self.assertEqual(widget_attrs['aria-label'], 'Category Name')

    def test_form_labels(self):
        """Test form field labels."""
        form = CategoryForm()
        self.assertEqual(form.fields['name'].label, 'Category Name')


class DeliveryFormTest(TestCase):
    """Test cases for the DeliveryForm."""

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
            description='Test laptop',
            category=self.category,
            quantity=10,
            price=999.99,
            vendor=self.vendor
        )

    def test_valid_form_with_existing_customer(self):
        """Test form with existing customer."""
        form_data = {
            'item': self.item.id,
            'existing_customer': self.customer.id,
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_valid_form_with_new_customer(self):
        """Test form with new customer data."""
        form_data = {
            'item': self.item.id,
            'new_customer_first_name': 'Jane',
            'new_customer_phone': '+1987654321',
            'new_customer_location': '456 Oak Ave',
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_form_both_existing_and_new_customer(self):
        """Test form validation when both existing and new customer are provided."""
        form_data = {
            'item': self.item.id,
            'existing_customer': self.customer.id,
            'new_customer_first_name': 'Jane',
            'new_customer_phone': '+1987654321',
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('Please either select an existing customer OR fill out the new customer details, not both.', 
                     form.errors['__all__'])

    def test_invalid_form_no_customer_data(self):
        """Test form validation when no customer data is provided."""
        form_data = {
            'item': self.item.id,
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('You must either select an existing customer or provide details for a new one.', 
                     form.errors['__all__'])

    def test_new_customer_missing_first_name(self):
        """Test validation when new customer is missing first name."""
        form_data = {
            'item': self.item.id,
            'new_customer_phone': '+1987654321',
            'new_customer_location': '456 Oak Ave',
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_customer_first_name', form.errors)
        self.assertIn('First Name is required for a new customer.', 
                     form.errors['new_customer_first_name'])

    def test_new_customer_missing_phone(self):
        """Test validation when new customer is missing phone."""
        form_data = {
            'item': self.item.id,
            'new_customer_first_name': 'Jane',
            'new_customer_location': '456 Oak Ave',
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_customer_phone', form.errors)
        self.assertIn('Phone Number is required for a new customer.', 
                     form.errors['new_customer_phone'])

    def test_required_fields(self):
        """Test that required fields are validated."""
        form = DeliveryForm(data={})
        self.assertFalse(form.is_valid())
        
        required_fields = ['item', 'date']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_form_field_widgets(self):
        """Test that form fields have correct widget classes."""
        form = DeliveryForm()
        
        self.assertEqual(form.fields['item'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['date'].widget.attrs['class'], 'form-control')
        self.assertEqual(form.fields['date'].widget.attrs['type'], 'datetime-local')
        self.assertEqual(form.fields['is_delivered'].widget.attrs['class'], 'form-check-input')

    def test_existing_customer_queryset_ordering(self):
        """Test that existing customer queryset is ordered by first name."""
        # Create another customer
        Customer.objects.create(
            first_name='Alice',
            last_name='Smith',
            email='alice@example.com',
            phone='+1555666777'
        )
        
        form = DeliveryForm()
        queryset = form.fields['existing_customer'].queryset
        customers = list(queryset)
        
        # Should be ordered by first_name
        self.assertEqual(customers[0].first_name, 'Alice')
        self.assertEqual(customers[1].first_name, 'John')

    def test_form_clean_method_with_partial_new_customer_data(self):
        """Test clean method with partial new customer data."""
        form_data = {
            'item': self.item.id,
            'new_customer_first_name': 'Jane',  # Only first name, missing phone
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
            'is_delivered': False
        }
        
        form = DeliveryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('new_customer_phone', form.errors)