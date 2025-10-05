"""
Test cases for store URL patterns.
"""

from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from accounts.models import Profile, UserRole
from store.models import Category, Item, Delivery
from store import views

User = get_user_model()


class StoreURLTest(TestCase):
    """Test cases for store URL patterns."""

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
        
        self.category = Category.objects.create(name='Electronics')
        
        self.item = Item.objects.create(
            name='Test Item',
            description='A test item',
            category=self.category,
            quantity=10,
            price=99.99
        )
        
        self.delivery = Delivery.objects.create(
            item=self.item,
            date='2024-01-01 10:00:00'
        )

    def test_dashboard_url(self):
        """Test dashboard URL pattern."""
        url = reverse('dashboard')
        self.assertEqual(url, '/store/')
        
        resolver = resolve('/store/')
        self.assertEqual(resolver.func, views.dashboard)

    def test_product_list_url(self):
        """Test product list URL pattern."""
        url = reverse('product-list')
        self.assertEqual(url, '/store/products/')
        
        resolver = resolve('/store/products/')
        self.assertEqual(resolver.func.view_class, views.ProductListView)

    def test_product_detail_url(self):
        """Test product detail URL pattern."""
        url = reverse('product-detail', kwargs={'slug': self.item.slug})
        expected_url = f'/store/product/{self.item.slug}/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.ProductDetailView)

    def test_product_create_url(self):
        """Test product create URL pattern."""
        url = reverse('product-create')
        self.assertEqual(url, '/store/product/create/')
        
        resolver = resolve('/store/product/create/')
        self.assertEqual(resolver.func.view_class, views.ProductCreateView)

    def test_product_update_url(self):
        """Test product update URL pattern."""
        url = reverse('product-update', kwargs={'slug': self.item.slug})
        expected_url = f'/store/product/{self.item.slug}/update/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.ProductUpdateView)

    def test_product_delete_url(self):
        """Test product delete URL pattern."""
        url = reverse('product-delete', kwargs={'slug': self.item.slug})
        expected_url = f'/store/product/{self.item.slug}/delete/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.ProductDeleteView)

    def test_category_list_url(self):
        """Test category list URL pattern."""
        url = reverse('category-list')
        self.assertEqual(url, '/store/categories/')
        
        resolver = resolve('/store/categories/')
        self.assertEqual(resolver.func.view_class, views.CategoryListView)

    def test_category_detail_url(self):
        """Test category detail URL pattern."""
        url = reverse('category-detail', kwargs={'pk': self.category.pk})
        expected_url = f'/store/category/{self.category.pk}/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.CategoryDetailView)

    def test_category_create_url(self):
        """Test category create URL pattern."""
        url = reverse('category-create')
        self.assertEqual(url, '/store/category/create/')
        
        resolver = resolve('/store/category/create/')
        self.assertEqual(resolver.func.view_class, views.CategoryCreateView)

    def test_category_update_url(self):
        """Test category update URL pattern."""
        url = reverse('category-update', kwargs={'pk': self.category.pk})
        expected_url = f'/store/category/{self.category.pk}/update/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.CategoryUpdateView)

    def test_category_delete_url(self):
        """Test category delete URL pattern."""
        url = reverse('category-delete', kwargs={'pk': self.category.pk})
        expected_url = f'/store/category/{self.category.pk}/delete/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.CategoryDeleteView)

    def test_deliveries_url(self):
        """Test deliveries list URL pattern."""
        url = reverse('deliveries')
        self.assertEqual(url, '/store/deliveries/')
        
        resolver = resolve('/store/deliveries/')
        self.assertEqual(resolver.func.view_class, views.DeliveryListView)

    def test_delivery_create_url(self):
        """Test delivery create URL pattern."""
        url = reverse('delivery-create')
        self.assertEqual(url, '/store/delivery/create/')
        
        resolver = resolve('/store/delivery/create/')
        self.assertEqual(resolver.func.view_class, views.DeliveryCreateView)

    def test_delivery_update_url(self):
        """Test delivery update URL pattern."""
        url = reverse('delivery-update', kwargs={'pk': self.delivery.pk})
        expected_url = f'/store/delivery/{self.delivery.pk}/update/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.DeliveryUpdateView)

    def test_delivery_delete_url(self):
        """Test delivery delete URL pattern."""
        url = reverse('delivery-delete', kwargs={'pk': self.delivery.pk})
        expected_url = f'/store/delivery/{self.delivery.pk}/delete/'
        self.assertEqual(url, expected_url)
        
        resolver = resolve(expected_url)
        self.assertEqual(resolver.func.view_class, views.DeliveryDeleteView)

    def test_url_name_resolution(self):
        """Test that all URL names can be resolved."""
        url_names = [
            'dashboard',
            'product-list',
            'product-create',
            'category-list',
            'category-create',
            'deliveries',
            'delivery-create',
        ]
        
        for url_name in url_names:
            with self.subTest(url_name=url_name):
                url = reverse(url_name)
                self.assertTrue(url.startswith('/store/'))

    def test_url_with_parameters_resolution(self):
        """Test URL patterns that require parameters."""
        url_patterns_with_params = [
            ('product-detail', {'slug': self.item.slug}),
            ('product-update', {'slug': self.item.slug}),
            ('product-delete', {'slug': self.item.slug}),
            ('category-detail', {'pk': self.category.pk}),
            ('category-update', {'pk': self.category.pk}),
            ('category-delete', {'pk': self.category.pk}),
            ('delivery-update', {'pk': self.delivery.pk}),
            ('delivery-delete', {'pk': self.delivery.pk}),
        ]
        
        for url_name, kwargs in url_patterns_with_params:
            with self.subTest(url_name=url_name):
                url = reverse(url_name, kwargs=kwargs)
                self.assertTrue(url.startswith('/store/'))

    def test_invalid_slug_url(self):
        """Test URL with invalid slug."""
        try:
            url = reverse('product-detail', kwargs={'slug': 'non-existent-slug'})
            # URL should be generated even with non-existent slug
            self.assertTrue(url.startswith('/store/product/'))
        except Exception as e:
            self.fail(f"URL generation should not fail with invalid slug: {e}")

    def test_invalid_pk_url(self):
        """Test URL with invalid primary key."""
        try:
            url = reverse('category-detail', kwargs={'pk': 99999})
            # URL should be generated even with non-existent pk
            self.assertTrue(url.startswith('/store/category/'))
        except Exception as e:
            self.fail(f"URL generation should not fail with invalid pk: {e}")


class URLPatternMatchingTest(TestCase):
    """Test that URL patterns match expected paths."""

    def test_root_store_url(self):
        """Test root store URL matches dashboard."""
        resolver = resolve('/store/')
        self.assertEqual(resolver.url_name, 'dashboard')

    def test_products_url_variants(self):
        """Test different product URL variants."""
        # Products list
        resolver = resolve('/store/products/')
        self.assertEqual(resolver.url_name, 'product-list')
        
        # Product detail
        resolver = resolve('/store/product/test-item/')
        self.assertEqual(resolver.url_name, 'product-detail')
        self.assertEqual(resolver.kwargs['slug'], 'test-item')
        
        # Product create
        resolver = resolve('/store/product/create/')
        self.assertEqual(resolver.url_name, 'product-create')

    def test_categories_url_variants(self):
        """Test different category URL variants."""
        # Categories list
        resolver = resolve('/store/categories/')
        self.assertEqual(resolver.url_name, 'category-list')
        
        # Category detail
        resolver = resolve('/store/category/1/')
        self.assertEqual(resolver.url_name, 'category-detail')
        self.assertEqual(resolver.kwargs['pk'], '1')
        
        # Category create
        resolver = resolve('/store/category/create/')
        self.assertEqual(resolver.url_name, 'category-create')

    def test_deliveries_url_variants(self):
        """Test different delivery URL variants."""
        # Deliveries list
        resolver = resolve('/store/deliveries/')
        self.assertEqual(resolver.url_name, 'deliveries')
        
        # Delivery create
        resolver = resolve('/store/delivery/create/')
        self.assertEqual(resolver.url_name, 'delivery-create')
        
        # Delivery update
        resolver = resolve('/store/delivery/1/update/')
        self.assertEqual(resolver.url_name, 'delivery-update')
        self.assertEqual(resolver.kwargs['pk'], '1')

    def test_slug_with_special_characters(self):
        """Test slug URL matching with special characters."""
        # Test slug with hyphens
        resolver = resolve('/store/product/test-item-with-hyphens/')
        self.assertEqual(resolver.url_name, 'product-detail')
        self.assertEqual(resolver.kwargs['slug'], 'test-item-with-hyphens')
        
        # Test slug with numbers
        resolver = resolve('/store/product/item-123/')
        self.assertEqual(resolver.url_name, 'product-detail')
        self.assertEqual(resolver.kwargs['slug'], 'item-123')

    def test_pk_url_matching(self):
        """Test primary key URL matching."""
        # Test various pk formats
        test_pks = ['1', '123', '999999']
        
        for pk in test_pks:
            with self.subTest(pk=pk):
                resolver = resolve(f'/store/category/{pk}/')
                self.assertEqual(resolver.url_name, 'category-detail')
                self.assertEqual(resolver.kwargs['pk'], pk)