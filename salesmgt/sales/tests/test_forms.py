"""
Test cases for sales forms (PurchaseForm, BootstrapMixin).
"""

from django.test import TestCase
from django.forms import widgets
from decimal import Decimal

from accounts.models import Vendor, User
from store.models import Category, Item
from sales.forms import PurchaseForm, BootstrapMixin
from sales.models import Purchase


class BootstrapMixinTest(TestCase):
    """Test cases for the BootstrapMixin."""

    def test_mixin_adds_form_control_class(self):
        """Test that mixin adds form-control class to field widgets."""
        
        class TestForm(BootstrapMixin):
            class Meta:
                model = Purchase
                fields = ['item', 'vendor', 'quantity']
        
        # Create test data
        vendor = Vendor.objects.create(
            name='Test Vendor',
            email='vendor@example.com',
            phone='+1234567890'
        )
        category = Category.objects.create(name='Electronics')
        item = Item.objects.create(
            name='Test Item',
            category=category,
            price=50.00
        )
        
        form = TestForm()
        
        # Check that form-control class is added to widgets
        for field_name, field in form.fields.items():
            if field_name not in ['delivery_date']:  # Exclude special cases
                self.assertIn('form-control', field.widget.attrs.get('class', ''))

    def test_mixin_preserves_existing_classes(self):
        """Test that mixin preserves existing CSS classes."""
        
        class TestForm(BootstrapMixin):
            class Meta:
                model = Purchase
                fields = ['quantity']
                widgets = {
                    'quantity': widgets.NumberInput(attrs={'class': 'existing-class'})
                }
        
        form = TestForm()
        
        # Should preserve existing class and add form-control
        widget_class = form.fields['quantity'].widget.attrs.get('class', '')
        self.assertIn('existing-class', widget_class)
        self.assertIn('form-control', widget_class)


class PurchaseFormTest(TestCase):
    """Test cases for the PurchaseForm."""

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
        
        self.item = Item.objects.create(
            name='Test Item',
            category=self.category,
            price=50.00,
            quantity=10
        )
        
        self.valid_form_data = {
            'item': self.item.id,
            'vendor': self.vendor.id,
            'price': '45.00',
            'description': 'Test purchase description',
            'quantity': 5,
            'delivery_status': 'P'
        }

    def test_valid_purchase_form(self):
        """Test form with valid data."""
        form = PurchaseForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())

    def test_purchase_form_save(self):
        """Test saving a valid form."""
        initial_quantity = self.item.quantity
        
        form = PurchaseForm(data=self.valid_form_data)
        self.assertTrue(form.is_valid())
        
        purchase = form.save()
        self.assertEqual(purchase.item, self.item)
        self.assertEqual(purchase.vendor, self.vendor)
        self.assertEqual(purchase.price, Decimal('45.00'))
        self.assertEqual(purchase.quantity, 5)
        self.assertEqual(purchase.description, 'Test purchase description')
        self.assertEqual(purchase.delivery_status, 'P')

    def test_form_fields_included(self):
        """Test that correct fields are included in the form."""
        form = PurchaseForm()
        expected_fields = [
            'item', 'price', 'description', 'vendor',
            'quantity', 'delivery_date', 'delivery_status'
        ]
        
        for field in expected_fields:
            self.assertIn(field, form.fields)

    def test_required_fields(self):
        """Test that required fields are validated."""
        form = PurchaseForm(data={})
        self.assertFalse(form.is_valid())
        
        # These fields should be required
        required_fields = ['item', 'vendor', 'price', 'quantity']
        for field in required_fields:
            self.assertIn(field, form.errors)

    def test_delivery_date_widget(self):
        """Test delivery date widget configuration."""
        form = PurchaseForm()
        delivery_date_widget = form.fields['delivery_date'].widget
        
        self.assertIsInstance(delivery_date_widget, widgets.DateInput)
        self.assertEqual(delivery_date_widget.attrs['class'], 'form-control')
        self.assertEqual(delivery_date_widget.attrs['type'], 'datetime-local')

    def test_description_widget(self):
        """Test description widget configuration."""
        form = PurchaseForm()
        description_widget = form.fields['description'].widget
        
        self.assertIsInstance(description_widget, widgets.Textarea)
        self.assertEqual(description_widget.attrs['rows'], 1)
        self.assertEqual(description_widget.attrs['cols'], 40)

    def test_quantity_widget(self):
        """Test quantity widget configuration."""
        form = PurchaseForm()
        quantity_widget = form.fields['quantity'].widget
        
        self.assertIsInstance(quantity_widget, widgets.NumberInput)
        self.assertEqual(quantity_widget.attrs['class'], 'form-control')

    def test_delivery_status_widget(self):
        """Test delivery status widget configuration."""
        form = PurchaseForm()
        delivery_status_widget = form.fields['delivery_status'].widget
        
        self.assertIsInstance(delivery_status_widget, widgets.Select)
        self.assertEqual(delivery_status_widget.attrs['class'], 'form-control')

    def test_price_widget(self):
        """Test price widget configuration."""
        form = PurchaseForm()
        price_widget = form.fields['price'].widget
        
        self.assertIsInstance(price_widget, widgets.NumberInput)
        self.assertEqual(price_widget.attrs['class'], 'form-control')

    def test_form_inherits_bootstrap_mixin(self):
        """Test that PurchaseForm inherits from BootstrapMixin."""
        self.assertTrue(issubclass(PurchaseForm, BootstrapMixin))

    def test_form_with_delivery_date(self):
        """Test form with delivery date."""
        from django.utils import timezone
        
        form_data = self.valid_form_data.copy()
        delivery_date = timezone.now() + timezone.timedelta(days=7)
        form_data['delivery_date'] = delivery_date.strftime('%Y-%m-%dT%H:%M')
        
        form = PurchaseForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_without_optional_fields(self):
        """Test form without optional fields."""
        minimal_data = {
            'item': self.item.id,
            'vendor': self.vendor.id,
            'price': '45.00',
            'quantity': 5,
            'delivery_status': 'P'
        }
        
        form = PurchaseForm(data=minimal_data)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_price(self):
        """Test form with invalid price."""
        form_data = self.valid_form_data.copy()
        form_data['price'] = 'invalid'
        
        form = PurchaseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('price', form.errors)

    def test_form_with_negative_quantity(self):
        """Test form with negative quantity."""
        form_data = self.valid_form_data.copy()
        form_data['quantity'] = -5
        
        form = PurchaseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('quantity', form.errors)

    def test_form_with_zero_quantity(self):
        """Test form with zero quantity."""
        form_data = self.valid_form_data.copy()
        form_data['quantity'] = 0
        
        form = PurchaseForm(data=form_data)
        # Zero quantity should be valid as it's allowed by PositiveIntegerField with default=0
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_delivery_status(self):
        """Test form with invalid delivery status."""
        form_data = self.valid_form_data.copy()
        form_data['delivery_status'] = 'INVALID'
        
        form = PurchaseForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('delivery_status', form.errors)

    def test_form_delivery_status_choices(self):
        """Test delivery status field choices."""
        form = PurchaseForm()
        delivery_status_field = form.fields['delivery_status']
        
        # Get choices from the field
        choices = delivery_status_field.choices
        choice_values = [choice[0] for choice in choices if choice[0]]  # Exclude empty choice
        
        # Should include P and S from DELIVERY_CHOICES
        self.assertIn('P', choice_values)
        self.assertIn('S', choice_values)

    def test_form_item_queryset(self):
        """Test that item field shows available items."""
        form = PurchaseForm()
        item_queryset = form.fields['item'].queryset
        
        self.assertIn(self.item, item_queryset)

    def test_form_vendor_queryset(self):
        """Test that vendor field shows available vendors."""
        form = PurchaseForm()
        vendor_queryset = form.fields['vendor'].queryset
        
        self.assertIn(self.vendor, vendor_queryset)

    def test_form_update_existing_purchase(self):
        """Test updating an existing purchase with the form."""
        # Create a purchase first
        purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            price=Decimal('30.00'),
            quantity=3,
            delivery_status='P'
        )
        
        # Update data
        update_data = {
            'item': self.item.id,
            'vendor': self.vendor.id,
            'price': '35.00',
            'quantity': 4,
            'delivery_status': 'S',
            'description': 'Updated description'
        }
        
        form = PurchaseForm(data=update_data, instance=purchase)
        self.assertTrue(form.is_valid())
        
        updated_purchase = form.save()
        self.assertEqual(updated_purchase.price, Decimal('35.00'))
        self.assertEqual(updated_purchase.quantity, 4)
        self.assertEqual(updated_purchase.delivery_status, 'S')
        self.assertEqual(updated_purchase.description, 'Updated description')

    def test_form_bootstrap_classes_applied(self):
        """Test that Bootstrap classes are applied to all relevant fields."""
        form = PurchaseForm()
        
        # Fields that should have form-control class
        form_control_fields = ['item', 'vendor', 'price', 'quantity', 'delivery_status']
        
        for field_name in form_control_fields:
            field = form.fields[field_name]
            widget_class = field.widget.attrs.get('class', '')
            self.assertIn('form-control', widget_class, 
                         f"Field {field_name} should have form-control class")

    def test_form_meta_model(self):
        """Test form meta model configuration."""
        self.assertEqual(PurchaseForm.Meta.model, Purchase)

    def test_form_excludes_auto_fields(self):
        """Test that auto-generated fields are not in the form."""
        form = PurchaseForm()
        
        # These fields should not be in the form as they're auto-generated
        excluded_fields = ['slug', 'order_date', 'total_value']
        
        for field in excluded_fields:
            self.assertNotIn(field, form.fields)