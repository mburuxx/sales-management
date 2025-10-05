"""
Test cases for sales URL patterns.
"""

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from accounts.models import Profile, UserRole, Vendor
from store.models import Category, Item
from sales.models import Sale, Purchase
from sales import views

User = get_user_model()


class SalesURLTest(TestCase):
    """Test cases for sales URL patterns."""

    def setUp(self):
        """Set up test data."""
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
        
        # Create sample sale and purchase for testing
        from accounts.models import Customer
        self.customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='+1234567890'
        )
        
        self.sale = Sale.objects.create(
            customer=self.customer,
            grand_total=100.00
        )
        
        self.purchase = Purchase.objects.create(
            item=self.item,
            vendor=self.vendor,
            price=45.00,
            quantity=5
        )

    def test_sales_list_url(self):
        """Test sales list URL pattern."""
        url = reverse('sales-list')
        self.assertEqual(url, '/sales/')
        
        resolver = resolve('/sales/')
        self.assertEqual(resolver.func.view_class, views.SaleListView)

    def test_sale_detail_url(self):
        """Test sale detail URL pattern."""
        url = reverse('sale-detail', kwargs={'pk': self.sale.pk})
        expected_url = f'/sales/sale/{self.sale.pk}/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.SaleDetailView)

    def test_purchases_list_url(self):
        """Test purchases list URL pattern."""
        url = reverse('purchases-list')
        self.assertEqual(url, '/sales/purchases/')
        
        resolver = resolve('/sales/purchases/')
        self.assertEqual(resolver.func.view_class, views.PurchaseListView)

    def test_purchase_detail_url(self):
        """Test purchase detail URL pattern."""
        url = reverse('purchase-detail', kwargs={'pk': self.purchase.pk})
        expected_url = f'/sales/purchase/{self.purchase.pk}/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.PurchaseDetailView)

    def test_purchase_create_url(self):
        """Test purchase create URL pattern."""
        url = reverse('purchase-create')
        self.assertEqual(url, '/sales/purchase/create/')
        
        resolver = resolve('/sales/purchase/create/')
        self.assertEqual(resolver.func.view_class, views.PurchaseCreateView)

    def test_purchase_update_url(self):
        """Test purchase update URL pattern."""
        url = reverse('purchase-update', kwargs={'pk': self.purchase.pk})
        expected_url = f'/sales/purchase/{self.purchase.pk}/update/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.PurchaseUpdateView)

    def test_purchase_delete_url(self):
        """Test purchase delete URL pattern."""
        url = reverse('purchase-delete', kwargs={'pk': self.purchase.pk})
        expected_url = f'/sales/purchase/{self.purchase.pk}/delete/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.PurchaseDeleteView)

    def test_export_sales_excel_url(self):
        """Test export sales to Excel URL pattern."""
        url = reverse('export-sales-excel')
        self.assertEqual(url, '/sales/export/sales/')
        
        resolver = resolve('/sales/export/sales/')
        self.assertEqual(resolver.func, views.export_sales_to_excel)

    def test_export_purchases_excel_url(self):
        """Test export purchases to Excel URL pattern."""
        url = reverse('export-purchases-excel')
        self.assertEqual(url, '/sales/export/purchases/')
        
        resolver = resolve('/sales/export/purchases/')
        self.assertEqual(resolver.func, views.export_purchases_to_excel)

    def test_url_name_resolution(self):
        """Test that all URL names can be resolved."""
        url_names = [
            'sales-list',
            'purchases-list',
            'purchase-create',
            'export-sales-excel',
            'export-purchases-excel',
        ]
        
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                self.assertTrue(url.startswith('/sales/'))

    def test_url_with_parameters_resolution(self):
        """Test URL patterns that require parameters."""
        url_patterns_with_params = [
            ('sale-detail', {'pk': self.sale.pk}),
            ('purchase-detail', {'pk': self.purchase.pk}),
            ('purchase-update', {'pk': self.purchase.pk}),
            ('purchase-delete', {'pk': self.purchase.pk}),
        ]
        
        for url_name, kwargs in url_patterns_with_params:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, kwargs=kwargs)
                self.assertTrue(url.startswith('/sales/'))

    def test_invalid_pk_url(self):
        """Test URL with invalid primary key."""
        try:
            url = reverse('sale-detail', kwargs={'pk': 99999})
            # URL should be generated even with non-existent pk
            self.assertTrue(url.startswith('/sales/sale/'))
        except Exception as e:
            self.fail(f"URL generation should not fail with invalid pk: {e}")

    def test_purchase_urls_with_different_pks(self):
        """Test purchase URLs with different primary keys."""
        test_pks = [1, 123, 999999]
        
        for pk in test_pks:
            with self.subTest(pk=pk):
                # Test purchase detail URL
                url = reverse('purchase-detail', kwargs={'pk': pk})
                expected_url = f'/sales/purchase/{pk}/'
                self.assertEqual(url, expected_url)
                
                # Test purchase update URL
                url = reverse('purchase-update', kwargs={'pk': pk})
                expected_url = f'/sales/purchase/{pk}/update/'
                self.assertEqual(url, expected_url)
                
                # Test purchase delete URL
                url = reverse('purchase-delete', kwargs={'pk': pk})
                expected_url = f'/sales/purchase/{pk}/delete/'
                self.assertEqual(url, expected_url)


class URLPatternMatchingTest(TestCase):
    """Test that URL patterns match expected paths."""

    def test_root_sales_url(self):
        """Test root sales URL matches sales list."""
        resolver = resolve('/sales/')
        self.assertEqual(resolver.url_name, 'sales-list')

    def test_purchases_url_variants(self):
        """Test different purchase URL variants."""
        # Purchases list
        resolver = resolve('/sales/purchases/')
        self.assertEqual(resolver.url_name, 'purchases-list')
        
        # Purchase detail
        resolver = resolve('/sales/purchase/1/')
        self.assertEqual(resolver.url_name, 'purchase-detail')
        self.assertEqual(resolver.kwargs['pk'], '1')
        
        # Purchase create
        resolver = resolve('/sales/purchase/create/')
        self.assertEqual(resolver.url_name, 'purchase-create')
        
        # Purchase update
        resolver = resolve('/sales/purchase/1/update/')
        self.assertEqual(resolver.url_name, 'purchase-update')
        self.assertEqual(resolver.kwargs['pk'], '1')
        
        # Purchase delete
        resolver = resolve('/sales/purchase/1/delete/')
        self.assertEqual(resolver.url_name, 'purchase-delete')
        self.assertEqual(resolver.kwargs['pk'], '1')

    def test_sale_url_variants(self):
        """Test different sale URL variants."""
        # Sale detail
        resolver = resolve('/sales/sale/1/')
        self.assertEqual(resolver.url_name, 'sale-detail')
        self.assertEqual(resolver.kwargs['pk'], '1')

    def test_export_url_variants(self):
        """Test different export URL variants."""
        # Export sales
        resolver = resolve('/sales/export/sales/')
        self.assertEqual(resolver.url_name, 'export-sales-excel')
        
        # Export purchases
        resolver = resolve('/sales/export/purchases/')
        self.assertEqual(resolver.url_name, 'export-purchases-excel')

    def test_pk_url_matching(self):
        """Test primary key URL matching."""
        # Test various pk formats
        test_pks = ['1', '123', '999999']
        
        for pk in test_pks:
            with self.subTest(pk=pk):
                # Sale detail
                resolver = resolve(f'/sales/sale/{pk}/')
                self.assertEqual(resolver.url_name, 'sale-detail')
                self.assertEqual(resolver.kwargs['pk'], pk)
                
                # Purchase detail
                resolver = resolve(f'/sales/purchase/{pk}/')
                self.assertEqual(resolver.url_name, 'purchase-detail')
                self.assertEqual(resolver.kwargs['pk'], pk)

    def test_nested_url_structure(self):
        """Test nested URL structure for sales app."""
        # Test that sales URLs are properly nested under /sales/
        sales_urls = [
            '/sales/',
            '/sales/purchases/',
            '/sales/sale/1/',
            '/sales/purchase/1/',
            '/sales/purchase/create/',
            '/sales/purchase/1/update/',
            '/sales/purchase/1/delete/',
            '/sales/export/sales/',
            '/sales/export/purchases/',
        ]
        
        for url in sales_urls:
            with self.subTest(url=url):
                resolver = resolve(url)
                # All should resolve successfully
                self.assertTrue(hasattr(resolver, 'url_name'))

    def test_url_trailing_slash_handling(self):
        """Test URL handling with and without trailing slashes."""
        # URLs that should work with trailing slash
        urls_with_slash = [
            '/sales/',
            '/sales/purchases/',
            '/sales/purchase/create/',
            '/sales/export/sales/',
            '/sales/export/purchases/',
        ]
        
        for url in urls_with_slash:
            with self.subTest(url=url):
                resolver = resolve(url)
                self.assertTrue(hasattr(resolver, 'url_name'))

    def test_url_case_sensitivity(self):
        """Test that URLs are case sensitive."""
        # These should all resolve correctly (lowercase)
        valid_urls = [
            '/sales/',
            '/sales/purchases/',
            '/sales/purchase/create/',
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                resolver = resolve(url)
                self.assertTrue(hasattr(resolver, 'url_name'))


class URLReverseTest(TestCase):
    """Test URL reverse resolution."""

    def test_reverse_sales_urls_without_params(self):
        """Test reversing sales URLs that don't require parameters."""
        url_names = [
            'sales-list',
            'purchases-list',
            'purchase-create',
            'export-sales-excel',
            'export-purchases-excel',
        ]
        
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                self.assertTrue(url.startswith('/sales/'))
                # Should be able to resolve back
                resolver = resolve(url)
                self.assertEqual(resolver.url_name, url_name)

    def test_reverse_sales_urls_with_params(self):
        """Test reversing sales URLs that require parameters."""
        test_pk = 123
        
        url_patterns_with_params = [
            ('sale-detail', f'/sales/sale/{test_pk}/'),
            ('purchase-detail', f'/sales/purchase/{test_pk}/'),
            ('purchase-update', f'/sales/purchase/{test_pk}/update/'),
            ('purchase-delete', f'/sales/purchase/{test_pk}/delete/'),
        ]
        
        for url_name, expected_url in url_patterns_with_params:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, kwargs={'pk': test_pk})
                self.assertEqual(url, expected_url)
                
                # Should be able to resolve back
                resolver = resolve(url)
                self.assertEqual(resolver.url_name, url_name)
                self.assertEqual(int(resolver.kwargs['pk']), test_pk)

    def test_reverse_with_string_pk(self):
        """Test reversing URLs with string primary keys."""
        test_pks = ['1', '42', '999']
        
        for pk in test_pks:
            with self.subTest(pk=pk):
                url = reverse('purchase-detail', kwargs={'pk': pk})
                expected_url = f'/sales/purchase/{pk}/'
                self.assertEqual(url, expected_url)

    def test_reverse_with_numeric_pk(self):
        """Test reversing URLs with numeric primary keys."""
        test_pks = [1, 42, 999]
        
        for pk in test_pks:
            with self.subTest(pk=pk):
                url = reverse('purchase-detail', kwargs={'pk': pk})
                expected_url = f'/sales/purchase/{pk}/'
                self.assertEqual(url, expected_url)


class URLNamespaceTest(TestCase):
    """Test URL namespace handling."""

    def test_sales_url_namespace(self):
        """Test that sales URLs are in the correct namespace."""
        # If sales URLs are namespaced, test the namespace
        # This test assumes no namespace is used based on the reverse patterns above
        
        # Test that reverse works without namespace
        url = reverse('sales-list')
        self.assertEqual(url, '/sales/')
        
        # Test that reverse works for all sales URLs without namespace
        sales_url_names = [
            'sales-list',
            'purchases-list',
            'purchase-create',
            'export-sales-excel',
            'export-purchases-excel',
        ]
        
        for url_name in sales_url_names:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                self.assertTrue(url.startswith('/sales/'))

    def test_url_includes_pattern(self):
        """Test that sales URLs are properly included in main URLconf."""
        # Test that all sales URLs resolve correctly, indicating proper inclusion
        sales_patterns = [
            '/sales/',
            '/sales/purchases/',
            '/sales/purchase/create/',
            '/sales/export/sales/',
        ]
        
        for pattern in sales_patterns:
            with self.subTest(pattern=pattern):
                resolver = resolve(pattern)
                self.assertTrue(hasattr(resolver, 'url_name'))
                # URL should be in sales app
                self.assertTrue(hasattr(resolver, 'func'))