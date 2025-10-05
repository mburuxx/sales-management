"""
Test cases for sales views.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils import timezone
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from accounts.models import Vendor, Customer, Profile, UserRole
from store.models import Category, Item
from sales.models import Sale, SaleDetail, Purchase
from sales.views import is_ajax, export_sales_to_excel, export_purchases_to_excel

User = get_user_model()


class UtilityFunctionTest(TestCase):
    """Test cases for utility functions."""

    def test_is_ajax_function_true(self):
        """Test is_ajax function returns True for AJAX requests."""
        mock_request = MagicMock()
        mock_request.META = {'HTTP_X_REQUESTED_WITH': 'XMLHttpRequest'}
        
        result = is_ajax(mock_request)
        self.assertTrue(result)

    def test_is_ajax_function_false(self):
        """Test is_ajax function returns False for non-AJAX requests."""
        mock_request = MagicMock()
        mock_request.META = {}
        
        result = is_ajax(mock_request)
        self.assertFalse(result)

    def test_is_ajax_function_none_value(self):
        """Test is_ajax function returns False when header is None."""
        mock_request = MagicMock()
        mock_request.META = {'HTTP_X_REQUESTED_WITH': None}
        
        result = is_ajax(mock_request)
        self.assertFalse(result)


class ExportSalesViewTest(TestCase):
    """Test cases for export_sales_to_excel view."""

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

    def test_export_sales_excel_response(self):
        """Test that export_sales_to_excel returns proper Excel response."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('export-sales-excel'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename=sales.xlsx'
        )

    def test_export_sales_excel_with_no_data(self):
        """Test export with no sales data."""
        # Delete the sale created in setUp
        self.sale.delete()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export-sales-excel'))
        
        self.assertEqual(response.status_code, 200)
        # Should still return Excel file even with no data

    @patch('sales.views.Workbook')
    def test_export_sales_excel_workbook_creation(self, mock_workbook):
        """Test that workbook is properly created and configured."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_workbook.return_value = mock_wb
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export-sales-excel'))
        
        # Verify workbook creation
        mock_workbook.assert_called_once()
        
        # Verify worksheet title is set
        self.assertEqual(mock_ws.title, 'Sales')
        
        # Verify headers are appended
        expected_headers = [
            'ID', 'Date', 'Customer', 'Sub Total',
            'Grand Total', 'Tax Amount', 'Tax Percentage',
            'Amount Paid', 'Amount Change'
        ]
        mock_ws.append.assert_any_call(expected_headers)


class ExportPurchasesViewTest(TestCase):
    """Test cases for export_purchases_to_excel view."""

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

    def test_export_purchases_excel_response(self):
        """Test that export_purchases_to_excel returns proper Excel response."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.get(reverse('export-purchases-excel'))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertEqual(
            response['Content-Disposition'],
            'attachment; filename=purchases.xlsx'
        )

    def test_export_purchases_excel_with_no_data(self):
        """Test export with no purchases data."""
        # Delete the purchase created in setUp
        self.purchase.delete()
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export-purchases-excel'))
        
        self.assertEqual(response.status_code, 200)
        # Should still return Excel file even with no data

    @patch('sales.views.Workbook')
    def test_export_purchases_excel_workbook_creation(self, mock_workbook):
        """Test that workbook is properly created and configured."""
        mock_wb = MagicMock()
        mock_ws = MagicMock()
        mock_wb.active = mock_ws
        mock_workbook.return_value = mock_wb
        
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('export-purchases-excel'))
        
        # Verify workbook creation
        mock_workbook.assert_called_once()
        
        # Verify worksheet title is set
        self.assertEqual(mock_ws.title, 'Purchases')
        
        # Verify headers are appended
        expected_headers = [
            'ID', 'Item', 'Description', 'Vendor', 'Order Date',
            'Delivery Date', 'Quantity', 'Delivery Status',
            'Price per item (Ksh)', 'Total Value'
        ]
        mock_ws.append.assert_any_call(expected_headers)


class SaleViewTest(TestCase):
    """Test cases for Sale-related views."""

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
            phone='+1234567890'
        )
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Test Item',
            category=self.category,
            price=50.00,
            quantity=10
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

    def test_sales_list_view_requires_login(self):
        """Test that sales list view requires authentication."""
        response = self.client.get(reverse('sales-list'))
        self.assertRedirects(response, '/accounts/login/?next=/sales/')

    def test_sales_list_view_with_authenticated_user(self):
        """Test sales list view with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sales-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sales')

    def test_sales_list_view_context_data(self):
        """Test that sales list view provides correct context data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('sales-list'))
        
        self.assertIn('object_list', response.context)
        self.assertIn(self.sale, response.context['object_list'])

    def test_sale_detail_view(self):
        """Test sale detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('sale-detail', kwargs={'pk': self.sale.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.sale)

    def test_sale_detail_view_with_invalid_pk(self):
        """Test sale detail view with invalid primary key."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('sale-detail', kwargs={'pk': 99999})
        )
        
        self.assertEqual(response.status_code, 404)


class PurchaseViewTest(TestCase):
    """Test cases for Purchase-related views."""

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

    def test_purchases_list_view_requires_login(self):
        """Test that purchases list view requires authentication."""
        response = self.client.get(reverse('purchases-list'))
        self.assertRedirects(response, '/accounts/login/?next=/sales/purchases/')

    def test_purchases_list_view_with_authenticated_user(self):
        """Test purchases list view with authenticated user."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('purchases-list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Purchases')

    def test_purchase_create_view_get(self):
        """Test GET request to purchase create view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('purchase-create'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create Purchase')

    def test_purchase_create_view_post_valid(self):
        """Test POST request to purchase create view with valid data."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'item': self.item.id,
            'vendor': self.vendor.id,
            'price': '40.00',
            'quantity': 3,
            'description': 'New test purchase',
            'delivery_status': 'P'
        }
        
        response = self.client.post(reverse('purchase-create'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Check that the purchase was created
        self.assertTrue(
            Purchase.objects.filter(description='New test purchase').exists()
        )

    def test_purchase_update_view(self):
        """Test purchase update view."""
        self.client.login(username='testuser', password='testpass123')
        
        form_data = {
            'item': self.item.id,
            'vendor': self.vendor.id,
            'price': '50.00',
            'quantity': 7,
            'description': 'Updated test purchase',
            'delivery_status': 'S'
        }
        
        response = self.client.post(
            reverse('purchase-update', kwargs={'pk': self.purchase.pk}),
            data=form_data
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the purchase was updated
        self.purchase.refresh_from_db()
        self.assertEqual(self.purchase.description, 'Updated test purchase')
        self.assertEqual(self.purchase.delivery_status, 'S')

    def test_purchase_delete_view(self):
        """Test purchase delete view."""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('purchase-delete', kwargs={'pk': self.purchase.pk})
        )
        
        self.assertEqual(response.status_code, 302)
        
        # Check that the purchase was deleted
        self.assertFalse(
            Purchase.objects.filter(id=self.purchase.id).exists()
        )

    def test_purchase_detail_view(self):
        """Test purchase detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('purchase-detail', kwargs={'pk': self.purchase.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.purchase)
        self.assertContains(response, 'Test purchase')


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

    def test_sales_list_permission(self):
        """Test sales list view permission."""
        self.url = reverse('sales-list')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()

    def test_purchases_list_permission(self):
        """Test purchases list view permission."""
        self.url = reverse('purchases-list')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()

    def test_export_sales_permission(self):
        """Test export sales view permission."""
        self.url = reverse('export-sales-excel')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()

    def test_export_purchases_permission(self):
        """Test export purchases view permission."""
        self.url = reverse('export-purchases-excel')
        self.test_view_requires_login()
        self.test_view_with_authenticated_user()


class ViewErrorHandlingTest(TestCase):
    """Test error handling in views."""

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

    def test_nonexistent_sale_detail(self):
        """Test accessing nonexistent sale detail."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('sale-detail', kwargs={'pk': 99999})
        )
        
        self.assertEqual(response.status_code, 404)

    def test_nonexistent_purchase_detail(self):
        """Test accessing nonexistent purchase detail."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('purchase-detail', kwargs={'pk': 99999})
        )
        
        self.assertEqual(response.status_code, 404)

    def test_invalid_purchase_update(self):
        """Test updating purchase with invalid data."""
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
        purchase = Purchase.objects.create(
            item=item,
            vendor=vendor,
            price=Decimal('45.00'),
            quantity=5
        )
        
        self.client.login(username='testuser', password='testpass123')
        
        # Try to update with invalid data
        form_data = {
            'item': item.id,
            'vendor': vendor.id,
            'price': 'invalid_price',  # Invalid price
            'quantity': 3,
            'delivery_status': 'P'
        }
        
        response = self.client.post(
            reverse('purchase-update', kwargs={'pk': purchase.pk}),
            data=form_data
        )
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error')  # Form should show errors


class AjaxRequestTest(TestCase):
    """Test AJAX request handling."""

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

    def test_ajax_request_detection(self):
        """Test AJAX request detection in views."""
        self.client.login(username='testuser', password='testpass123')
        
        # Make an AJAX request
        response = self.client.get(
            reverse('sales-list'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Response should be successful
        self.assertEqual(response.status_code, 200)

    def test_non_ajax_request(self):
        """Test regular (non-AJAX) request handling."""
        self.client.login(username='testuser', password='testpass123')
        
        # Make a regular request
        response = self.client.get(reverse('sales-list'))
        
        # Response should be successful
        self.assertEqual(response.status_code, 200)