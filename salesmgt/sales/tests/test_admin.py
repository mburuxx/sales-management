"""
Test cases for sales admin configuration.
"""

from django.test import TestCase
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from decimal import Decimal

from accounts.models import Vendor, Customer
from store.models import Category, Item
from sales.models import Sale, SaleDetail, Purchase
from sales.admin import SaleAdmin, SaleDetailAdmin, PurchaseAdmin

User = get_user_model()


class MockRequest:
    """Mock request object for admin testing."""
    pass


class SaleAdminTest(TestCase):
    """Test cases for SaleAdmin."""

    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = SaleAdmin(Sale, self.site)
        
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            sub_total=Decimal('100.00'),
            grand_total=Decimal('110.00'),
            tax_amount=Decimal('10.00'),
            tax_percentage=10.0,
            amount_paid=Decimal('110.00'),
            amount_change=Decimal('0.00')
        )

    def test_sale_admin_registration(self):
        """Test that SaleAdmin is properly configured."""
        self.assertIsInstance(self.admin, SaleAdmin)

    def test_sale_list_display(self):
        """Test list display fields."""
        expected_fields = ['id', 'customer', 'date_added', 'grand_total', 'amount_paid']
        if hasattr(self.admin, 'list_display'):
            for field in expected_fields:
                self.assertIn(field, self.admin.list_display)

    def test_sale_list_filter(self):
        """Test list filter fields."""
        expected_filters = ['date_added', 'customer']
        if hasattr(self.admin, 'list_filter'):
            for filter_field in expected_filters:
                self.assertIn(filter_field, self.admin.list_filter)

    def test_sale_search_fields(self):
        """Test search fields."""
        expected_search_fields = ['customer__first_name', 'customer__last_name', 'customer__email']
        if hasattr(self.admin, 'search_fields'):
            for field in expected_search_fields:
                self.assertIn(field, self.admin.search_fields)

    def test_sale_readonly_fields(self):
        """Test readonly fields."""
        if hasattr(self.admin, 'readonly_fields'):
            # Date added should typically be readonly since it's auto-generated
            self.assertIn('date_added', self.admin.readonly_fields)

    def test_sale_ordering(self):
        """Test default ordering."""
        if hasattr(self.admin, 'ordering'):
            # Should typically be ordered by date (newest first)
            self.assertIn('-date_added', self.admin.ordering)

    def test_sale_date_hierarchy(self):
        """Test date hierarchy."""
        if hasattr(self.admin, 'date_hierarchy'):
            self.assertEqual(self.admin.date_hierarchy, 'date_added')


class SaleDetailAdminTest(TestCase):
    """Test cases for SaleDetailAdmin."""

    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = SaleDetailAdmin(SaleDetail, self.site)
        
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
        
        self.sale_detail = SaleDetail.objects.create(
            sale=self.sale,
            item=self.item,
            price=Decimal('50.00'),
            quantity=2,
            total_detail=Decimal('100.00')
        )

    def test_sale_detail_admin_registration(self):
        """Test that SaleDetailAdmin is properly configured."""
        self.assertIsInstance(self.admin, SaleDetailAdmin)

    def test_sale_detail_list_display(self):
        """Test list display fields."""
        expected_fields = ['sale', 'item', 'quantity', 'price', 'total_detail']
        if hasattr(self.admin, 'list_display'):
            for field in expected_fields:
                self.assertIn(field, self.admin.list_display)

    def test_sale_detail_list_filter(self):
        """Test list filter fields."""
        expected_filters = ['sale', 'item']
        if hasattr(self.admin, 'list_filter'):
            for filter_field in expected_filters:
                self.assertIn(filter_field, self.admin.list_filter)

    def test_sale_detail_search_fields(self):
        """Test search fields."""
        if hasattr(self.admin, 'search_fields'):
            # Should be able to search by item name or sale info
            search_fields = self.admin.search_fields
            self.assertTrue(
                any('item' in field for field in search_fields) or
                any('sale' in field for field in search_fields)
            )


class PurchaseAdminTest(TestCase):
    """Test cases for PurchaseAdmin."""

    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.admin = PurchaseAdmin(Purchase, self.site)
        
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
        
        self.purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            price=Decimal('45.00'),
            quantity=5,
            description='Test purchase'
        )

    def test_purchase_admin_registration(self):
        """Test that PurchaseAdmin is properly configured."""
        self.assertIsInstance(self.admin, PurchaseAdmin)

    def test_purchase_list_display(self):
        """Test list display fields."""
        expected_fields = ['item', 'vendor', 'quantity', 'price', 'total_value', 'order_date', 'delivery_status']
        if hasattr(self.admin, 'list_display'):
            for field in expected_fields:
                self.assertIn(field, self.admin.list_display)

    def test_purchase_list_filter(self):
        """Test list filter fields."""
        expected_filters = ['vendor', 'delivery_status', 'order_date']
        if hasattr(self.admin, 'list_filter'):
            for filter_field in expected_filters:
                self.assertIn(filter_field, self.admin.list_filter)

    def test_purchase_search_fields(self):
        """Test search fields."""
        expected_search_fields = ['item__name', 'vendor__name', 'description']
        if hasattr(self.admin, 'search_fields'):
            for field in expected_search_fields:
                self.assertIn(field, self.admin.search_fields)

    def test_purchase_readonly_fields(self):
        """Test readonly fields."""
        if hasattr(self.admin, 'readonly_fields'):
            # These fields should typically be readonly
            readonly_fields = ['slug', 'order_date', 'total_value']
            for field in readonly_fields:
                self.assertIn(field, self.admin.readonly_fields)

    def test_purchase_prepopulated_fields(self):
        """Test prepopulated fields for slug."""
        if hasattr(self.admin, 'prepopulated_fields'):
            self.assertEqual(self.admin.prepopulated_fields.get('slug'), ['vendor'])

    def test_purchase_ordering(self):
        """Test default ordering."""
        if hasattr(self.admin, 'ordering'):
            # Should be ordered by order_date as defined in model
            self.assertIn('-order_date', self.admin.ordering)

    def test_purchase_date_hierarchy(self):
        """Test date hierarchy."""
        if hasattr(self.admin, 'date_hierarchy'):
            self.assertEqual(self.admin.date_hierarchy, 'order_date')

    def test_purchase_fieldsets(self):
        """Test admin fieldsets if defined."""
        if hasattr(self.admin, 'fieldsets'):
            # Flatten all fields from fieldsets
            all_fields = []
            for fieldset in self.admin.fieldsets:
                if isinstance(fieldset[1]['fields'], (list, tuple)):
                    all_fields.extend(fieldset[1]['fields'])
                else:
                    # Handle single fields or nested structures
                    all_fields.append(fieldset[1]['fields'])
            
            expected_fields = ['item', 'vendor', 'price', 'quantity', 'description', 'delivery_status']
            for field in expected_fields:
                self.assertIn(field, all_fields)


class AdminModelStringRepresentationTest(TestCase):
    """Test string representations of models in admin."""

    def setUp(self):
        """Set up test data."""
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
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

    def test_sale_string_representation(self):
        """Test sale string representation in admin."""
        sale = Sale.objects.create(
            customer=self.customer,
            grand_total=Decimal('110.00')
        )
        
        expected_str = f"Sale ID: {sale.id} | Grand Total: 110.00 | Date: {sale.date_added}"
        self.assertEqual(str(sale), expected_str)

    def test_sale_detail_string_representation(self):
        """Test sale detail string representation in admin."""
        sale = Sale.objects.create(
            customer=self.customer,
            grand_total=Decimal('100.00')
        )
        
        sale_detail = SaleDetail.objects.create(
            sale=sale,
            item=self.item,
            price=Decimal('50.00'),
            quantity=2,
            total_detail=Decimal('100.00')
        )
        
        expected_str = f"Detail ID: {sale_detail.id} | Sale ID: {sale.id} | Quantity: 2"
        self.assertEqual(str(sale_detail), expected_str)

    def test_purchase_string_representation(self):
        """Test purchase string representation in admin."""
        purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            price=Decimal('45.00'),
            quantity=5
        )
        
        # Purchase __str__ returns item name
        self.assertEqual(str(purchase), self.item.name)


class AdminPermissionTest(TestCase):
    """Test admin permissions and access."""

    def setUp(self):
        """Set up test data."""
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='userpass123'
        )
        
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@example.com',
            password='staffpass123',
            is_staff=True
        )

    def test_superuser_admin_access(self):
        """Test that superuser can access admin."""
        self.assertTrue(self.superuser.is_superuser)
        self.assertTrue(self.superuser.is_staff)

    def test_staff_user_admin_access(self):
        """Test that staff user can access admin."""
        self.assertTrue(self.staff_user.is_staff)
        self.assertFalse(self.staff_user.is_superuser)

    def test_regular_user_no_admin_access(self):
        """Test that regular user cannot access admin."""
        self.assertFalse(self.regular_user.is_staff)
        self.assertFalse(self.regular_user.is_superuser)


class AdminCustomMethodsTest(TestCase):
    """Test custom methods in admin classes."""

    def setUp(self):
        """Set up test data."""
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

    def test_purchase_admin_total_value_display(self):
        """Test if admin displays total value correctly."""
        site = AdminSite()
        admin = PurchaseAdmin(Purchase, site)
        
        purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            price=Decimal('45.00'),
            quantity=5
        )
        
        # If there's a custom method to display total value
        if hasattr(admin, 'get_total_value'):
            total_value = admin.get_total_value(purchase)
            self.assertEqual(total_value, Decimal('225.00'))

    def test_sale_admin_customer_display(self):
        """Test custom customer display in sale admin."""
        customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        sale = Sale.objects.create(
            customer=customer,
            grand_total=Decimal('100.00')
        )
        
        site = AdminSite()
        admin = SaleAdmin(Sale, site)
        
        # If there's a custom method to display customer info
        if hasattr(admin, 'get_customer_info'):
            customer_info = admin.get_customer_info(sale)
            self.assertIn('John Doe', customer_info)

    def test_admin_list_per_page(self):
        """Test list per page setting."""
        site = AdminSite()
        sale_admin = SaleAdmin(Sale, site)
        purchase_admin = PurchaseAdmin(Purchase, site)
        
        # Check if list_per_page is set
        if hasattr(sale_admin, 'list_per_page'):
            self.assertIsInstance(sale_admin.list_per_page, int)
            self.assertGreater(sale_admin.list_per_page, 0)
        
        if hasattr(purchase_admin, 'list_per_page'):
            self.assertIsInstance(purchase_admin.list_per_page, int)
            self.assertGreater(purchase_admin.list_per_page, 0)

    def test_admin_actions(self):
        """Test custom admin actions if any."""
        site = AdminSite()
        purchase_admin = PurchaseAdmin(Purchase, site)
        
        # Check if custom actions are defined
        if hasattr(purchase_admin, 'actions'):
            self.assertIsInstance(purchase_admin.actions, (list, tuple))

    def test_admin_inlines(self):
        """Test admin inlines if any."""
        site = AdminSite()
        sale_admin = SaleAdmin(Sale, site)
        
        # Check if inlines are defined (e.g., SaleDetail inline in Sale admin)
        if hasattr(sale_admin, 'inlines'):
            self.assertIsInstance(sale_admin.inlines, (list, tuple))

    def test_admin_form_customization(self):
        """Test custom form configuration."""
        site = AdminSite()
        purchase_admin = PurchaseAdmin(Purchase, site)
        
        # Check if custom form is specified
        if hasattr(purchase_admin, 'form'):
            from django import forms
            self.assertTrue(issubclass(purchase_admin.form, forms.ModelForm))

    def test_admin_list_editable(self):
        """Test list editable fields."""
        site = AdminSite()
        purchase_admin = PurchaseAdmin(Purchase, site)
        
        # Check if list_editable is defined
        if hasattr(purchase_admin, 'list_editable'):
            self.assertIsInstance(purchase_admin.list_editable, (list, tuple))
            # Editable fields should also be in list_display
            for field in purchase_admin.list_editable:
                self.assertIn(field, purchase_admin.list_display)

    def test_admin_list_display_links(self):
        """Test list display links configuration."""
        site = AdminSite()
        sale_admin = SaleAdmin(Sale, site)
        
        # Check if list_display_links is customized
        if hasattr(sale_admin, 'list_display_links'):
            self.assertIsInstance(sale_admin.list_display_links, (list, tuple))
            # Display links should be in list_display
            for field in sale_admin.list_display_links:
                self.assertIn(field, sale_admin.list_display)