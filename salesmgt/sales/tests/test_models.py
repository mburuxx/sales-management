"""
Test cases for sales models (Sale, SaleDetail, Purchase).
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from accounts.models import Vendor, Customer, User
from store.models import Category, Item
from sales.models import Sale, SaleDetail, Purchase, DELIVERY_CHOICES


class SaleModelTest(TestCase):
    """Test cases for the Sale model."""

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
        
        self.sale_data = {
            'customer': self.customer,
            'sub_total': Decimal('100.00'),
            'grand_total': Decimal('110.00'),
            'tax_amount': Decimal('10.00'),
            'tax_percentage': 10.0,
            'amount_paid': Decimal('110.00'),
            'amount_change': Decimal('0.00')
        }

    def test_sale_creation(self):
        """Test creating a new sale."""
        sale = Sale.objects.create(**self.sale_data)
        
        self.assertEqual(sale.customer, self.customer)
        self.assertEqual(sale.sub_total, Decimal('100.00'))
        self.assertEqual(sale.grand_total, Decimal('110.00'))
        self.assertEqual(sale.tax_amount, Decimal('10.00'))
        self.assertEqual(sale.tax_percentage, 10.0)
        self.assertEqual(sale.amount_paid, Decimal('110.00'))
        self.assertEqual(sale.amount_change, Decimal('0.00'))
        self.assertTrue(sale.date_added)

    def test_sale_str_representation(self):
        """Test string representation of sale."""
        sale = Sale.objects.create(**self.sale_data)
        expected_str = (
            f"Sale ID: {sale.id} | "
            f"Grand Total: 110.00 | "
            f"Date: {sale.date_added}"
        )
        self.assertEqual(str(sale), expected_str)

    def test_sale_default_values(self):
        """Test default values for sale fields."""
        sale = Sale.objects.create(customer=self.customer)
        
        self.assertEqual(sale.sub_total, Decimal('0.0'))
        self.assertEqual(sale.grand_total, Decimal('0.0'))
        self.assertEqual(sale.tax_amount, Decimal('0.0'))
        self.assertEqual(sale.tax_percentage, 0.0)
        self.assertEqual(sale.amount_paid, Decimal('0.0'))
        self.assertEqual(sale.amount_change, Decimal('0.0'))

    def test_sale_date_added_auto_now_add(self):
        """Test that date_added is automatically set."""
        before_creation = timezone.now()
        sale = Sale.objects.create(**self.sale_data)
        after_creation = timezone.now()
        
        self.assertGreaterEqual(sale.date_added, before_creation)
        self.assertLessEqual(sale.date_added, after_creation)

    def test_sale_customer_do_nothing_on_delete(self):
        """Test that sale is not deleted when customer is deleted."""
        sale = Sale.objects.create(**self.sale_data)
        customer_id = self.customer.id
        
        # This should not delete the sale due to DO_NOTHING
        self.customer.delete()
        
        sale.refresh_from_db()
        self.assertEqual(sale.customer_id, customer_id)
        # Customer object will be None but the ID remains
        self.assertIsNone(sale.customer)

    def test_sale_sum_products_empty(self):
        """Test sum_products method with no sale details."""
        sale = Sale.objects.create(**self.sale_data)
        self.assertEqual(sale.sum_products(), 0)

    def test_sale_sum_products_with_details(self):
        """Test sum_products method with sale details."""
        sale = Sale.objects.create(**self.sale_data)
        
        # Create test items and sale details
        category = Category.objects.create(name='Electronics')
        item1 = Item.objects.create(
            name='Item 1',
            category=category,
            price=50.00,
            quantity=10
        )
        item2 = Item.objects.create(
            name='Item 2',
            category=category,
            price=30.00,
            quantity=5
        )
        
        SaleDetail.objects.create(
            sale=sale,
            item=item1,
            price=Decimal('50.00'),
            quantity=2,
            total_detail=Decimal('100.00')
        )
        SaleDetail.objects.create(
            sale=sale,
            item=item2,
            price=Decimal('30.00'),
            quantity=3,
            total_detail=Decimal('90.00')
        )
        
        self.assertEqual(sale.sum_products(), 5)  # 2 + 3

    def test_sale_meta_options(self):
        """Test model meta options."""
        self.assertEqual(Sale._meta.db_table, 'sales')
        self.assertEqual(Sale._meta.verbose_name, 'Sale')
        self.assertEqual(Sale._meta.verbose_name_plural, 'Sales')


class SaleDetailModelTest(TestCase):
    """Test cases for the SaleDetail model."""

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
            phone='+1234567890'
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            grand_total=Decimal('100.00')
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Test Item',
            category=self.category,
            price=50.00,
            quantity=10
        )
        
        self.sale_detail_data = {
            'sale': self.sale,
            'item': self.item,
            'price': Decimal('50.00'),
            'quantity': 2,
            'total_detail': Decimal('100.00')
        }

    def test_sale_detail_creation(self):
        """Test creating a new sale detail."""
        sale_detail = SaleDetail.objects.create(**self.sale_detail_data)
        
        self.assertEqual(sale_detail.sale, self.sale)
        self.assertEqual(sale_detail.item, self.item)
        self.assertEqual(sale_detail.price, Decimal('50.00'))
        self.assertEqual(sale_detail.quantity, 2)
        self.assertEqual(sale_detail.total_detail, Decimal('100.00'))

    def test_sale_detail_str_representation(self):
        """Test string representation of sale detail."""
        sale_detail = SaleDetail.objects.create(**self.sale_detail_data)
        expected_str = (
            f"Detail ID: {sale_detail.id} | "
            f"Sale ID: {self.sale.id} | "
            f"Quantity: 2"
        )
        self.assertEqual(str(sale_detail), expected_str)

    def test_sale_detail_cascade_delete_with_sale(self):
        """Test that sale detail is deleted when sale is deleted."""
        sale_detail = SaleDetail.objects.create(**self.sale_detail_data)
        sale_detail_id = sale_detail.id
        
        self.sale.delete()
        
        with self.assertRaises(SaleDetail.DoesNotExist):
            SaleDetail.objects.get(id=sale_detail_id)

    def test_sale_detail_do_nothing_on_item_delete(self):
        """Test that sale detail remains when item is deleted."""
        sale_detail = SaleDetail.objects.create(**self.sale_detail_data)
        item_id = self.item.id
        
        # This should not delete the sale detail due to DO_NOTHING
        self.item.delete()
        
        sale_detail.refresh_from_db()
        self.assertEqual(sale_detail.item_id, item_id)
        # Item object will be None but the ID remains
        self.assertIsNone(sale_detail.item)

    def test_sale_detail_positive_quantity(self):
        """Test that quantity is a positive integer."""
        sale_detail_data = self.sale_detail_data.copy()
        sale_detail_data['quantity'] = 5
        
        sale_detail = SaleDetail.objects.create(**sale_detail_data)
        self.assertEqual(sale_detail.quantity, 5)

    def test_sale_detail_related_name(self):
        """Test the related name for sale details."""
        sale_detail = SaleDetail.objects.create(**self.sale_detail_data)
        
        # Test that we can access sale details from sale using the related name
        sale_details = self.sale.saledetail_set.all()
        self.assertEqual(sale_details.count(), 1)
        self.assertEqual(sale_details.first(), sale_detail)

    def test_sale_detail_meta_options(self):
        """Test model meta options."""
        self.assertEqual(SaleDetail._meta.db_table, 'sale_details')
        self.assertEqual(SaleDetail._meta.verbose_name, 'Sale Detail')
        self.assertEqual(SaleDetail._meta.verbose_name_plural, 'Sale Details')


class PurchaseModelTest(TestCase):
    """Test cases for the Purchase model."""

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
            quantity=5  # Initial quantity
        )
        
        self.purchase_data = {
            'item': self.item,
            'vendor': self.vendor,
            'description': 'Test purchase description',
            'quantity': 10,
            'price': Decimal('45.00'),
            'delivery_status': 'P'
        }

    def test_purchase_creation(self):
        """Test creating a new purchase."""
        initial_quantity = self.item.quantity
        
        purchase = Purchase.objects.create(**self.purchase_data)
        
        self.assertEqual(purchase.item, self.item)
        self.assertEqual(purchase.vendor, self.vendor)
        self.assertEqual(purchase.description, 'Test purchase description')
        self.assertEqual(purchase.quantity, 10)
        self.assertEqual(purchase.price, Decimal('45.00'))
        self.assertEqual(purchase.delivery_status, 'P')
        self.assertEqual(purchase.total_value, Decimal('450.00'))  # 45 * 10
        self.assertTrue(purchase.slug)
        self.assertTrue(purchase.order_date)

    def test_purchase_save_calculates_total_value(self):
        """Test that save method calculates total value."""
        purchase = Purchase.objects.create(**self.purchase_data)
        expected_total = self.purchase_data['price'] * self.purchase_data['quantity']
        self.assertEqual(purchase.total_value, expected_total)

    def test_purchase_save_updates_item_quantity(self):
        """Test that save method updates item quantity."""
        initial_quantity = self.item.quantity
        
        purchase = Purchase.objects.create(**self.purchase_data)
        
        # Refresh item from database
        self.item.refresh_from_db()
        expected_quantity = initial_quantity + self.purchase_data['quantity']
        self.assertEqual(self.item.quantity, expected_quantity)

    def test_purchase_str_representation(self):
        """Test string representation of purchase."""
        purchase = Purchase.objects.create(**self.purchase_data)
        self.assertEqual(str(purchase), self.item.name)

    def test_purchase_slug_generation(self):
        """Test that slug is generated from vendor."""
        purchase = Purchase.objects.create(**self.purchase_data)
        self.assertTrue(purchase.slug)
        # Slug should be based on vendor name
        self.assertIn('test-vendor', purchase.slug.lower())

    def test_purchase_default_values(self):
        """Test default values for purchase fields."""
        purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor
        )
        
        self.assertEqual(purchase.quantity, 0)
        self.assertEqual(purchase.price, Decimal('0.0'))
        self.assertEqual(purchase.delivery_status, 'P')
        self.assertEqual(purchase.total_value, Decimal('0.0'))

    def test_purchase_delivery_choices(self):
        """Test delivery status choices."""
        # Test pending status
        purchase_pending = Purchase.objects.create(
            **self.purchase_data,
            delivery_status='P'
        )
        self.assertEqual(purchase_pending.delivery_status, 'P')
        
        # Test successful status
        purchase_successful = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            quantity=5,
            price=Decimal('30.00'),
            delivery_status='S'
        )
        self.assertEqual(purchase_successful.delivery_status, 'S')

    def test_purchase_with_delivery_date(self):
        """Test purchase with delivery date."""
        delivery_date = timezone.now() + timedelta(days=7)
        purchase_data = self.purchase_data.copy()
        purchase_data['delivery_date'] = delivery_date
        
        purchase = Purchase.objects.create(**purchase_data)
        self.assertEqual(purchase.delivery_date, delivery_date)

    def test_purchase_order_date_auto_now_add(self):
        """Test that order_date is automatically set."""
        before_creation = timezone.now()
        purchase = Purchase.objects.create(**self.purchase_data)
        after_creation = timezone.now()
        
        self.assertGreaterEqual(purchase.order_date, before_creation)
        self.assertLessEqual(purchase.order_date, after_creation)

    def test_purchase_cascade_delete_with_item(self):
        """Test that purchase is deleted when item is deleted."""
        purchase = Purchase.objects.create(**self.purchase_data)
        purchase_id = purchase.id
        
        self.item.delete()
        
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(id=purchase_id)

    def test_purchase_cascade_delete_with_vendor(self):
        """Test that purchase is deleted when vendor is deleted."""
        purchase = Purchase.objects.create(**self.purchase_data)
        purchase_id = purchase.id
        
        self.vendor.delete()
        
        with self.assertRaises(Purchase.DoesNotExist):
            Purchase.objects.get(id=purchase_id)

    def test_purchase_meta_ordering(self):
        """Test that purchases are ordered by order_date."""
        # Create purchases at different times
        purchase1 = Purchase.objects.create(**self.purchase_data)
        
        # Create second purchase with different vendor to avoid slug conflicts
        vendor2 = Vendor.objects.create(
            name='Second Vendor',
            email='vendor2@example.com',
            phone='+1234567891'
        )
        
        purchase_data_2 = self.purchase_data.copy()
        purchase_data_2['vendor'] = vendor2
        purchase2 = Purchase.objects.create(**purchase_data_2)
        
        purchases = list(Purchase.objects.all())
        # Should be ordered by order_date (ascending)
        self.assertEqual(purchases[0].order_date, purchase1.order_date)
        self.assertEqual(purchases[1].order_date, purchase2.order_date)

    def test_purchase_positive_quantity_field(self):
        """Test that quantity is a positive integer field."""
        purchase_data = self.purchase_data.copy()
        purchase_data['quantity'] = 15
        
        purchase = Purchase.objects.create(**purchase_data)
        self.assertEqual(purchase.quantity, 15)

    def test_purchase_vendor_related_name(self):
        """Test the related name for purchases from vendor."""
        purchase = Purchase.objects.create(**self.purchase_data)
        
        # Test that we can access purchases from vendor using the related name
        vendor_purchases = self.vendor.purchases.all()
        self.assertEqual(vendor_purchases.count(), 1)
        self.assertEqual(vendor_purchases.first(), purchase)

    def test_delivery_choices_constant(self):
        """Test the DELIVERY_CHOICES constant."""
        expected_choices = [("P", "Pending"), ("S", "Successful")]
        self.assertEqual(DELIVERY_CHOICES, expected_choices)

    def test_purchase_decimal_field_precision(self):
        """Test decimal field precision for price and total_value."""
        purchase_data = self.purchase_data.copy()
        purchase_data['price'] = Decimal('99.99')
        purchase_data['quantity'] = 3
        
        purchase = Purchase.objects.create(**purchase_data)
        
        # Check that decimal fields maintain precision
        self.assertEqual(purchase.price, Decimal('99.99'))
        self.assertEqual(purchase.total_value, Decimal('299.97'))

    def test_purchase_update_recalculates_total(self):
        """Test that updating purchase recalculates total value."""
        purchase = Purchase.objects.create(**self.purchase_data)
        
        # Update price and quantity
        purchase.price = Decimal('60.00')
        purchase.quantity = 8
        purchase.save()
        
        # Total should be recalculated
        self.assertEqual(purchase.total_value, Decimal('480.00'))  # 60 * 8